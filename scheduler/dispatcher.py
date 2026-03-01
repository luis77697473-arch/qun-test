"""
Dispatcher Module — Predictive Feedback-Controlled Task Router
================================================================

The Dispatcher is the central coordinator that:
  1. Receives incoming tasks from external producers.
  2. Consults the Monitor's latest dispatch weights (w_i^{adj}).
  3. Routes each task to a Worker using **weighted random selection**
     proportional to the predicted performance scores.
  4. Handles task failures by delegating to the DeadlockDetector's
     retry mechanism with exponential back-off.

Feedback Control Loop
---------------------
The Dispatcher implements a closed-loop control cycle:

    ┌──────────┐      tasks       ┌────────────┐
    │ Producer │ ───────────────▸ │ Dispatcher  │
    └──────────┘                  └──────┬──────┘
                                         │  weighted
                                         │  selection
                    ┌────────────────────┼────────────────────┐
                    ▼                    ▼                    ▼
              ┌──────────┐        ┌──────────┐        ┌──────────┐
              │ Worker 0 │        │ Worker 1 │        │ Worker 2 │
              └────┬─────┘        └────┬─────┘        └────┬─────┘
                   │ latency           │ latency           │ latency
                   ▼                   ▼                   ▼
              ┌─────────────────────────────────────────────────┐
              │                   Monitor                       │
              │  WMA ─▸ Score ─▸ Trend Adjust ─▸ Weights       │
              └────────────────────────┬────────────────────────┘
                                       │  w_i^{adj}
                                       ▼
                              ┌──────────────┐
                              │  Dispatcher   │  (loop)
                              └──────────────┘
"""

import random
import threading
import time
from typing import Optional

from scheduler.worker import Task, TaskResult, Worker, SharedResource
from scheduler.monitor import Monitor
from scheduler.deadlock import DeadlockDetector


class Dispatcher:
    """
    Routes tasks to Workers using Monitor-provided dispatch weights.

    Parameters
    ----------
    workers : list[Worker]
        The pool of worker nodes.
    monitor : Monitor
        The monitoring module that publishes dispatch weights.
    deadlock_detector : DeadlockDetector
        Handles deadlock resolution and retry scheduling.
    shared_resources : list[SharedResource]
        Global shared resources injected into each worker.
    """

    def __init__(
        self,
        workers: list[Worker],
        monitor: Monitor,
        deadlock_detector: DeadlockDetector,
        shared_resources: Optional[list[SharedResource]] = None,
    ):
        self.workers = {w.worker_id: w for w in workers}
        self.monitor = monitor
        self.deadlock_detector = deadlock_detector

        # Current dispatch weights — updated by Monitor callback
        self._weights: dict[str, float] = {}
        self._weights_lock = threading.Lock()

        # Task tracking
        self._total_dispatched = 0
        self._total_succeeded = 0
        self._total_failed = 0
        self._results: list[TaskResult] = []
        self._results_lock = threading.Lock()

        # Shared resources
        resource_registry: dict[str, SharedResource] = {}
        for res in (shared_resources or []):
            resource_registry[res.resource_id] = res

        # Inject resource registry and result callback into each worker
        for w in workers:
            w._resource_registry = resource_registry
            w.on_result = self._on_task_result

        # Register workers with the monitor
        for w in workers:
            monitor.register_worker(w.worker_id, w)

        # Wire up monitor callback
        monitor.on_weights_updated = self._on_weights_updated

        # Wire up deadlock resolution
        deadlock_detector.on_deadlock_resolved = self._on_deadlock_victim

    # ---------------------------------------------------------------
    # Weight updates from Monitor
    # ---------------------------------------------------------------

    def _on_weights_updated(self, weights: dict[str, float]) -> None:
        with self._weights_lock:
            self._weights = dict(weights)

    # ---------------------------------------------------------------
    # Task result callback
    # ---------------------------------------------------------------

    def _on_task_result(self, result: TaskResult) -> None:
        # Feed latency back to the Monitor
        self.monitor.record_latency(result.worker_id, result.latency)

        with self._results_lock:
            self._results.append(result)
            if result.success:
                self._total_succeeded += 1
            else:
                self._total_failed += 1
                # Schedule retry via deadlock detector
                self._handle_failure(result)

    def _handle_failure(self, result: TaskResult) -> None:
        """Re-dispatch a failed task after exponential back-off."""
        # Reconstruct a minimal task for retry
        task = Task(task_id=result.task_id, payload_size=0.5)
        delay = self.deadlock_detector.schedule_retry(task)
        if delay is not None:
            # Retry after delay in a background thread
            threading.Thread(
                target=self._retry_after_delay,
                args=(task, delay),
                daemon=True,
            ).start()

    def _retry_after_delay(self, task: Task, delay: float) -> None:
        time.sleep(delay)
        self.dispatch(task)

    # ---------------------------------------------------------------
    # Deadlock victim callback
    # ---------------------------------------------------------------

    def _on_deadlock_victim(self, victim_worker_id: str) -> None:
        """Called when a worker is selected as a deadlock victim."""
        # The worker's current pending tasks remain in its queue;
        # just clear the wait-for edges so it can proceed.
        pass

    # ---------------------------------------------------------------
    # Core dispatch logic
    # ---------------------------------------------------------------

    def dispatch(self, task: Task) -> str:
        """
        Dispatch a task to the best-suited worker based on current weights.
        Returns the worker_id that received the task.

        Uses weighted random selection:  P(worker_i) = w_i^{adj}
        Falls back to round-robin if no weights are available yet.
        """
        with self._weights_lock:
            weights = dict(self._weights)

        worker_ids = list(self.workers.keys())

        if weights and sum(weights.values()) > 0:
            ids = list(weights.keys())
            ws = [weights[wid] for wid in ids]
            chosen_id = random.choices(ids, weights=ws, k=1)[0]
        else:
            # Fallback: pick the worker with fewest pending tasks
            chosen_id = min(worker_ids, key=lambda wid: self.workers[wid].pending_tasks)

        worker = self.workers[chosen_id]
        if not worker.submit(task):
            # Queue full — try another worker
            for wid in worker_ids:
                if wid != chosen_id and self.workers[wid].submit(task):
                    chosen_id = wid
                    break
            else:
                # All queues full — schedule retry
                delay = self.deadlock_detector.schedule_retry(task)
                if delay is not None:
                    threading.Thread(
                        target=self._retry_after_delay,
                        args=(task, delay),
                        daemon=True,
                    ).start()

        with self._results_lock:
            self._total_dispatched += 1
        return chosen_id

    def dispatch_batch(self, tasks: list[Task]) -> dict[str, int]:
        """Dispatch a batch of tasks. Returns counts per worker."""
        counts: dict[str, int] = {wid: 0 for wid in self.workers}
        for task in tasks:
            wid = self.dispatch(task)
            counts[wid] = counts.get(wid, 0) + 1
        return counts

    # ---------------------------------------------------------------
    # Metrics
    # ---------------------------------------------------------------

    @property
    def total_dispatched(self) -> int:
        with self._results_lock:
            return self._total_dispatched

    @property
    def total_succeeded(self) -> int:
        with self._results_lock:
            return self._total_succeeded

    @property
    def total_failed(self) -> int:
        with self._results_lock:
            return self._total_failed

    @property
    def results(self) -> list[TaskResult]:
        with self._results_lock:
            return list(self._results)
