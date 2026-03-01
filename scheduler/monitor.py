"""
Monitor Module — Real-Time Metrics & WMA Load Prediction
==========================================================

The Monitor continuously collects per-worker latency samples and computes
a *Weighted Moving Average (WMA)* to predict future load pressure.

Mathematical Foundation (LaTeX)
-------------------------------

### 1. Weighted Moving Average (WMA)

Given the most recent *n* latency observations for worker *i*:

    L_i = [l_1, l_2, ..., l_n]

The WMA assigns linearly increasing weights to more recent observations:

    WMA_i = \\frac{\\sum_{k=1}^{n} k \\cdot l_k}{\\sum_{k=1}^{n} k}
          = \\frac{\\sum_{k=1}^{n} k \\cdot l_k}{\\frac{n(n+1)}{2}}

This gives higher influence to the latest samples, making the estimator
responsive to sudden load changes while smoothing out noise.

### 2. Performance Volatility (\\Delta T)

We measure how *unstable* a worker's performance is via the coefficient
of variation of the recent window:

    \\Delta T_i = \\frac{\\sigma(L_i)}{\\mu(L_i) + \\epsilon}

where \\epsilon is a small constant (1e-9) to prevent division by zero.

### 3. Composite Performance Score

Each worker receives a score that balances *speed* (inverse average latency)
and *stability* (inverse volatility):

    S_i = \\alpha \\cdot \\frac{1}{T_{avg,i}} + (1 - \\alpha) \\cdot \\frac{1}{\\Delta T_i + \\epsilon}

where:
  - T_{avg,i} = WMA_i  (the weighted moving average latency)
  - \\Delta T_i          (the performance volatility)
  - \\alpha \\in [0, 1]   (tuning knob: 0 = pure-stability, 1 = pure-speed)

### 4. Derivation of the Normalised Dispatch Weight

To convert scores into dispatch probabilities, we normalise across all *N* workers:

    w_i = \\frac{S_i}{\\sum_{j=1}^{N} S_j}

So the Dispatcher assigns a fraction w_i of incoming tasks to worker i.

### 5. Trend-Based Predictive Adjustment

We augment the static score with a linear trend term.  Let \\beta be the
slope of a least-squares fit over the recent WMA history for worker i:

    \\beta_i = \\frac{n \\sum k \\cdot WMA_k - (\\sum k)(\\sum WMA_k)}
              {n \\sum k^2 - (\\sum k)^2}

If \\beta_i > 0 the worker's latency is *increasing* (degrading), so we
penalise its score:

    S_i^{adj} = S_i \\cdot \\max(0.1, \\; 1 - \\gamma \\cdot \\beta_i)

where \\gamma is the trend sensitivity parameter.

Full final dispatch weight after adjustment:

    w_i^{adj} = \\frac{S_i^{adj}}{\\sum_{j=1}^{N} S_j^{adj}}
"""

import threading
import time
import math
from collections import deque
from dataclasses import dataclass, field


# ---------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------

@dataclass
class WorkerSnapshot:
    """Point-in-time snapshot of a worker's predicted performance."""
    worker_id: str
    wma_latency: float        # Weighted moving average latency
    volatility: float         # Performance volatility (ΔT)
    trend_slope: float        # β — positive means degrading
    score: float              # Raw composite score S_i
    adjusted_score: float     # Trend-adjusted score S_i^adj
    dispatch_weight: float    # Normalised dispatch probability w_i
    pending_tasks: int
    tasks_processed: int
    timestamp: float = field(default_factory=time.monotonic)


class WorkerMetrics:
    """Thread-safe rolling metrics for a single worker."""

    def __init__(self, worker_id: str, window_size: int = 50):
        self.worker_id = worker_id
        self.window_size = window_size
        self._latencies: deque[float] = deque(maxlen=window_size)
        self._wma_history: deque[float] = deque(maxlen=window_size)
        self._lock = threading.Lock()

    def record(self, latency: float) -> None:
        with self._lock:
            self._latencies.append(latency)
            self._wma_history.append(self._compute_wma_unlocked())

    # ---------------------------------------------------------------
    # WMA calculation  (called under lock)
    # ---------------------------------------------------------------

    def _compute_wma_unlocked(self) -> float:
        """
        WMA = sum(k * l_k) / sum(k)  for k = 1..n
        """
        n = len(self._latencies)
        if n == 0:
            return 0.0
        numerator = sum((k + 1) * lat for k, lat in enumerate(self._latencies))
        denominator = n * (n + 1) / 2
        return numerator / denominator

    # ---------------------------------------------------------------
    # Public computed properties
    # ---------------------------------------------------------------

    def wma_latency(self) -> float:
        with self._lock:
            return self._compute_wma_unlocked()

    def _volatility_unlocked(self) -> float:
        """ΔT = σ(L) / (μ(L) + ε)  — must be called with self._lock held."""
        if len(self._latencies) < 2:
            return 0.0
        lats = list(self._latencies)
        mean = sum(lats) / len(lats)
        var = sum((x - mean) ** 2 for x in lats) / len(lats)
        std = math.sqrt(var)
        return std / (mean + 1e-9)

    def volatility(self) -> float:
        """ΔT = σ(L) / (μ(L) + ε)"""
        with self._lock:
            return self._volatility_unlocked()

    def _trend_slope_unlocked(self) -> float:
        """Least-squares slope β — must be called with self._lock held."""
        history = list(self._wma_history)
        n = len(history)
        if n < 3:
            return 0.0
        sum_k = sum(range(1, n + 1))
        sum_k2 = sum(k * k for k in range(1, n + 1))
        sum_y = sum(history)
        sum_ky = sum((k + 1) * y for k, y in enumerate(history))
        denom = n * sum_k2 - sum_k * sum_k
        if denom == 0:
            return 0.0
        return (n * sum_ky - sum_k * sum_y) / denom

    def trend_slope(self) -> float:
        """
        Least-squares slope β over the WMA history.
        β > 0  ⟹  latency increasing (worker degrading)
        β < 0  ⟹  latency decreasing (worker improving)
        """
        with self._lock:
            return self._trend_slope_unlocked()

    def snapshot(self) -> tuple[float, float, float]:
        """Return (wma_latency, volatility, trend_slope) under a single lock acquisition."""
        with self._lock:
            wma = self._compute_wma_unlocked()
            vol = self._volatility_unlocked()
            trend = self._trend_slope_unlocked()
        return wma, vol, trend


class Monitor:
    """
    Central monitoring module.

    Periodically computes per-worker performance scores and publishes
    normalised dispatch weights for the Dispatcher to consume.

    Parameters
    ----------
    alpha : float
        Speed-vs-stability trade-off (0 = pure stability, 1 = pure speed).
    gamma : float
        Trend sensitivity for predictive adjustment.
    window_size : int
        Number of recent latency samples kept per worker.
    """

    def __init__(
        self,
        alpha: float = 0.6,
        gamma: float = 5.0,
        window_size: int = 50,
    ):
        self.alpha = alpha
        self.gamma = gamma
        self.window_size = window_size

        self._workers: dict[str, WorkerMetrics] = {}
        self._latest_snapshots: dict[str, WorkerSnapshot] = {}
        self._lock = threading.Lock()
        self._running = False
        self._thread = None

        # Callback for external consumers (e.g. Dispatcher)
        self.on_weights_updated = None
        # Store reference to worker objects for pending_tasks / tasks_processed
        self._worker_objects = {}

    # ---------------------------------------------------------------
    # Registration
    # ---------------------------------------------------------------

    def register_worker(self, worker_id: str, worker_obj=None) -> None:
        with self._lock:
            self._workers[worker_id] = WorkerMetrics(worker_id, self.window_size)
            if worker_obj:
                self._worker_objects[worker_id] = worker_obj

    # ---------------------------------------------------------------
    # Data ingestion
    # ---------------------------------------------------------------

    def record_latency(self, worker_id: str, latency: float) -> None:
        with self._lock:
            metrics = self._workers.get(worker_id)
        if metrics:
            metrics.record(latency)

    # ---------------------------------------------------------------
    # Score computation
    # ---------------------------------------------------------------

    def compute_scores(self) -> dict[str, WorkerSnapshot]:
        """
        Compute composite scores and normalised dispatch weights
        for all registered workers.
        """
        eps = 1e-9
        with self._lock:
            worker_ids = list(self._workers.keys())
            metrics_map = dict(self._workers)

        snapshots: dict[str, WorkerSnapshot] = {}
        raw_scores: dict[str, float] = {}
        adj_scores: dict[str, float] = {}

        for wid in worker_ids:
            m = metrics_map[wid]
            t_avg, delta_t, beta = m.snapshot()
            t_avg = t_avg or eps

            # S_i = α / T_avg + (1-α) / (ΔT + ε)
            score = self.alpha / (t_avg + eps) + (1 - self.alpha) / (delta_t + eps)

            # Trend adjustment: penalise if β > 0
            adjustment = max(0.1, 1.0 - self.gamma * max(0, beta))
            adj_score = score * adjustment

            raw_scores[wid] = score
            adj_scores[wid] = adj_score

            worker_obj = self._worker_objects.get(wid)
            snapshots[wid] = WorkerSnapshot(
                worker_id=wid,
                wma_latency=t_avg,
                volatility=delta_t,
                trend_slope=beta,
                score=score,
                adjusted_score=adj_score,
                dispatch_weight=0.0,  # filled below
                pending_tasks=worker_obj.pending_tasks if worker_obj else 0,
                tasks_processed=worker_obj.tasks_processed if worker_obj else 0,
            )

        # Normalise weights
        total = sum(adj_scores.values()) or 1.0
        for wid in worker_ids:
            snapshots[wid].dispatch_weight = adj_scores[wid] / total

        with self._lock:
            self._latest_snapshots = snapshots

        if self.on_weights_updated:
            weights = {wid: s.dispatch_weight for wid, s in snapshots.items()}
            self.on_weights_updated(weights)

        return snapshots

    # ---------------------------------------------------------------
    # Periodic refresh loop
    # ---------------------------------------------------------------

    def start(self, interval: float = 0.2) -> None:
        self._running = True
        self._thread = threading.Thread(
            target=self._loop, args=(interval,), name="monitor", daemon=True
        )
        self._thread.start()

    def stop(self) -> None:
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)

    def _loop(self, interval: float) -> None:
        while self._running:
            self.compute_scores()
            time.sleep(interval)

    # ---------------------------------------------------------------
    # Accessors
    # ---------------------------------------------------------------

    @property
    def latest_snapshots(self) -> dict[str, WorkerSnapshot]:
        with self._lock:
            return dict(self._latest_snapshots)
