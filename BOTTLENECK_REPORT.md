# Performance Bottleneck Analysis Report

> Auto-generated analysis of the Distributed Task Scheduler codebase.

---

## Executive Summary

A systematic scan of all modules (`worker.py`, `monitor.py`, `dispatcher.py`,
`deadlock.py`, `main.py`) identified **14 potential bottlenecks** spanning lock
contention, algorithmic complexity, memory efficiency, and thread safety.

---

## Critical Findings

### 1. [CRITICAL] Monitor — 3N Lock Acquisitions Per Scoring Cycle

**File:** `scheduler/monitor.py:247-250`

In `compute_scores()`, each call to `wma_latency()`, `volatility()`, and
`trend_slope()` individually acquires `WorkerMetrics._lock`. For *N* workers,
this causes **3N lock acquisitions** every 150 ms.

```python
for wid in worker_ids:
    m = metrics_map[wid]
    t_avg = m.wma_latency()    # Lock #1
    delta_t = m.volatility()   # Lock #2
    beta = m.trend_slope()     # Lock #3
```

**Fix:** Add a single `snapshot()` method to `WorkerMetrics` that returns all
three values under one lock acquisition.

---

### 2. [CRITICAL] Dispatcher — Unprotected Counter Increment

**File:** `scheduler/dispatcher.py:202`

`_total_dispatched += 1` is not protected by any lock. The `+=` operation in
CPython is not atomic and can lose increments under concurrent access.

```python
self._total_dispatched += 1  # RACE: no lock
```

**Fix:** Move inside `_results_lock` or use `threading.Lock` for counters.

---

### 3. [CRITICAL] Worker — Unsafe `qsize()` Read

**File:** `scheduler/worker.py:200-201`

`pending_tasks` reads `task_queue.qsize()` without synchronisation. While
`Queue.qsize()` is thread-safe in CPython due to the GIL, it returns an
approximate value and is documented as unreliable for control flow.

**Fix:** Track an explicit atomic counter incremented on `put` and decremented
after `get`.

---

## High Severity Findings

### 4. [HIGH] Worker — Lock Per Task Completion

**File:** `scheduler/worker.py:139-141`

Every processed task acquires `self._lock` to update two counters. Under high
throughput this becomes a hot contention point.

**Fix:** Use thread-local accumulators flushed periodically, or `threading`-free
atomic integers.

---

### 5. [HIGH] Dispatcher — Full Dict Copy on Every Dispatch

**File:** `scheduler/dispatcher.py:172-173`

```python
with self._weights_lock:
    weights = dict(self._weights)  # Copy on every call
```

With 200+ tasks this creates 200+ dict allocations under lock.

**Fix:** Use copy-on-write: store an immutable reference and swap atomically.
The reader never needs a lock.

---

### 6. [HIGH] Monitor — 4-Pass Trend Slope Calculation

**File:** `scheduler/monitor.py:160-163`

`trend_slope()` makes four separate passes over the history deque
(`sum_k`, `sum_k2`, `sum_y`, `sum_ky`). With `window_size=50`, this runs
~200 iterations per call.

**Fix:** Maintain running accumulators (`sum_k`, `sum_ky`, etc.) that update
incrementally when new samples arrive.

---

### 7. [HIGH] Deadlock — O(n) `list.index()` Inside DFS

**File:** `scheduler/deadlock.py:115`

```python
idx = path.index(neighbour)  # Linear scan
```

Inside the recursive DFS, `path.index()` is O(n). Replace with a
`dict[str, int]` mapping node → position.

---

### 8. [HIGH] SharedResource — Unprotected `owner` Field

**File:** `scheduler/worker.py:50,55,59`

`self.owner` is read and written without holding the resource lock, creating a
check-then-act race between `try_acquire` and `release`.

**Fix:** Access `self.owner` only while `self.lock` is held (it already is in
`try_acquire`, but `release` checks before acquiring).

---

## Medium Severity Findings

### 9. [MEDIUM] Dispatcher — Unbounded Results List

**File:** `scheduler/dispatcher.py:85,125`

`self._results` grows without bound. For long-running simulations this is a
memory leak.

**Fix:** Use `collections.deque(maxlen=N)` or periodically flush old results.

---

### 10. [MEDIUM] Dispatcher — Thread-Per-Retry Overhead

**File:** `scheduler/dispatcher.py:140-144`

A new `threading.Thread` is created for every retry. Thread creation is
expensive (~1 ms each).

**Fix:** Use `concurrent.futures.ThreadPoolExecutor` with a bounded pool, or a
single retry-scheduler thread with a priority queue.

---

### 11. [MEDIUM] Monitor — Triple-Pass Volatility Calculation

**File:** `scheduler/monitor.py:138-147`

`volatility()` copies the deque to a list, then iterates twice (mean, variance).

**Fix:** Use Welford's online algorithm to compute mean and variance in a single
pass, updated incrementally on each `record()`.

---

### 12. [MEDIUM] Main — Polling Wait Loop

**File:** `main.py:205-209`

```python
while time.monotonic() < deadline:
    total_pending = sum(w.pending_tasks for w in workers)
    time.sleep(0.2)
```

Polls every 200 ms. Could be replaced with a `threading.Event` or
`Condition` signalled when the last worker's queue drains.

---

### 13. [MEDIUM] Main — Repeated List Comprehension in Task Generation

**File:** `main.py:187-189`

```python
required = random.sample(
    [r.resource_id for r in resources], k=num_res
)
```

The list `[r.resource_id for r in resources]` is rebuilt for every task.

**Fix:** Pre-compute `resource_ids = [r.resource_id for r in resources]` once.

---

## Low Severity Findings

### 14. [LOW] Worker — Silent RuntimeError in `release()`

**File:** `scheduler/worker.py:62-64`

```python
except RuntimeError:
    pass  # Silently swallowed
```

Could mask real locking bugs. Add a log warning.

---

## Summary Table

| #  | Severity | Module       | Issue                              | Lines     |
|----|----------|--------------|------------------------------------|-----------|
| 1  | CRITICAL | monitor.py   | 3N lock acquisitions per cycle     | 247-250   |
| 2  | CRITICAL | dispatcher.py| Unprotected counter increment      | 202       |
| 3  | CRITICAL | worker.py    | Unsafe qsize() for control flow    | 200-201   |
| 4  | HIGH     | worker.py    | Lock contention per task           | 139-141   |
| 5  | HIGH     | dispatcher.py| Dict copy under lock per dispatch  | 172-173   |
| 6  | HIGH     | monitor.py   | 4-pass trend slope calculation     | 160-163   |
| 7  | HIGH     | deadlock.py  | O(n) path.index() in DFS           | 115       |
| 8  | HIGH     | worker.py    | Unprotected SharedResource.owner   | 50,55,59  |
| 9  | MEDIUM   | dispatcher.py| Unbounded results list             | 85,125    |
| 10 | MEDIUM   | dispatcher.py| Thread-per-retry overhead          | 140-144   |
| 11 | MEDIUM   | monitor.py   | Triple-pass volatility calc        | 138-147   |
| 12 | MEDIUM   | main.py      | Polling wait loop                  | 205-209   |
| 13 | MEDIUM   | main.py      | Repeated list comprehension        | 187-189   |
| 14 | LOW      | worker.py    | Silent RuntimeError swallow        | 62-64     |

---

## Recommended Remediation Roadmap

1. **Phase 1 — Critical:** Fix race conditions (items 2, 3) and consolidate
   Monitor lock acquisitions (item 1).
2. **Phase 2 — High:** Optimise algorithmic hotspots (items 6, 7, 11) and
   fix SharedResource thread safety (item 8).
3. **Phase 3 — Medium:** Bound collections (item 9), use thread pools for
   retries (item 10), and event-based signalling (item 12).
4. **Phase 4 — Low:** Improve error logging (item 14).
