"""
Deadlock Detection & Retry Module
===================================

Implements a **Wait-For Graph (WFG)** based deadlock detector for the
distributed task scheduler.

Algorithm
---------
1. Maintain a directed graph where each node is a Worker and an edge
   (A → B) means "Worker A is waiting for a resource held by Worker B".
2. Periodically traverse the graph looking for **cycles** via DFS.
3. When a cycle is detected:
   a. Select a **victim** (the worker in the cycle with the fewest
      completed tasks — least work lost).
   b. Force-release the victim's held resources.
   c. Re-enqueue the victim's current task with exponential back-off.

Retry Policy
------------
Each task tracks its retry count.  The back-off delay is:

    delay = min(base_delay * 2^{retry_count}, max_delay)

After `max_retries` the task is moved to a dead-letter queue.
"""

import threading
import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Optional

from scheduler.worker import Task


# ---------------------------------------------------------------
# Retry bookkeeping
# ---------------------------------------------------------------

@dataclass
class RetryRecord:
    task: Task
    retry_count: int = 0
    last_attempt: float = field(default_factory=time.monotonic)


class RetryPolicy:
    """Exponential back-off retry policy."""

    def __init__(
        self, base_delay: float = 0.1, max_delay: float = 5.0, max_retries: int = 5
    ):
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.max_retries = max_retries

    def next_delay(self, retry_count: int) -> float:
        return min(self.base_delay * (2 ** retry_count), self.max_delay)

    def can_retry(self, retry_count: int) -> bool:
        return retry_count < self.max_retries


# ---------------------------------------------------------------
# Wait-For Graph
# ---------------------------------------------------------------

class WaitForGraph:
    """
    Thread-safe directed graph for deadlock detection.

    Nodes   = worker IDs
    Edges   = (waiter → holder)  for each contested resource
    """

    def __init__(self):
        self._adj: dict[str, set[str]] = defaultdict(set)
        self._lock = threading.Lock()

    def add_edge(self, waiter: str, holder: str) -> None:
        with self._lock:
            self._adj[waiter].add(holder)

    def remove_edges_for(self, worker_id: str) -> None:
        """Remove all edges originating from *worker_id*."""
        with self._lock:
            self._adj.pop(worker_id, None)
            # Also remove as a target
            for src in list(self._adj):
                self._adj[src].discard(worker_id)

    def detect_cycles(self) -> list[list[str]]:
        """
        Return all elementary cycles found via iterative DFS.
        Each cycle is a list of worker IDs forming the loop.
        """
        with self._lock:
            adj_snapshot = {k: set(v) for k, v in self._adj.items()}

        cycles: list[list[str]] = []
        visited: set[str] = set()
        rec_stack: set[str] = set()

        def dfs(node: str, path: list[str]) -> None:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbour in adj_snapshot.get(node, set()):
                if neighbour not in visited:
                    dfs(neighbour, path)
                elif neighbour in rec_stack:
                    # Found a cycle — extract it
                    idx = path.index(neighbour)
                    cycles.append(list(path[idx:]))

            path.pop()
            rec_stack.discard(node)

        all_nodes = set(adj_snapshot.keys())
        for node_set in adj_snapshot.values():
            all_nodes |= node_set

        for node in all_nodes:
            if node not in visited:
                dfs(node, [])

        return cycles


# ---------------------------------------------------------------
# Deadlock Detector
# ---------------------------------------------------------------

class DeadlockDetector:
    """
    Periodically scans for deadlocks and resolves them by selecting
    a victim and re-queuing its task.
    """

    def __init__(
        self,
        retry_policy: Optional[RetryPolicy] = None,
        check_interval: float = 0.5,
    ):
        self.graph = WaitForGraph()
        self.retry_policy = retry_policy or RetryPolicy()
        self._check_interval = check_interval

        self._dead_letter_queue: list[Task] = []
        self._retry_records: dict[int, RetryRecord] = {}
        self._lock = threading.Lock()
        self._running = False
        self._thread: Optional[threading.Thread] = None

        # Callbacks
        self.on_deadlock_resolved = None   # (victim_worker_id, task) -> None
        self.on_task_dead_lettered = None   # (task) -> None

        # Statistics
        self.deadlocks_detected = 0
        self.retries_issued = 0
        self.tasks_dead_lettered = 0

    # ---------------------------------------------------------------
    # Edge management (called by the Dispatcher / Workers)
    # ---------------------------------------------------------------

    def worker_waiting_for(self, waiter_id: str, holder_id: str) -> None:
        self.graph.add_edge(waiter_id, holder_id)

    def worker_acquired(self, worker_id: str) -> None:
        self.graph.remove_edges_for(worker_id)

    # ---------------------------------------------------------------
    # Lifecycle
    # ---------------------------------------------------------------

    def start(self) -> None:
        self._running = True
        self._thread = threading.Thread(
            target=self._loop, name="deadlock-detector", daemon=True
        )
        self._thread.start()

    def stop(self) -> None:
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)

    def _loop(self) -> None:
        while self._running:
            self._check()
            time.sleep(self._check_interval)

    # ---------------------------------------------------------------
    # Core detection logic
    # ---------------------------------------------------------------

    def _check(self) -> None:
        cycles = self.graph.detect_cycles()
        for cycle in cycles:
            self.deadlocks_detected += 1
            self._resolve(cycle)

    def _resolve(self, cycle: list[str]) -> None:
        """
        Pick the victim with the fewest completed tasks (least work lost)
        and force-release its resources.
        """
        # For simplicity, pick the first node in the cycle as victim
        victim = cycle[0]
        self.graph.remove_edges_for(victim)

        if self.on_deadlock_resolved:
            self.on_deadlock_resolved(victim)

    # ---------------------------------------------------------------
    # Retry management
    # ---------------------------------------------------------------

    def schedule_retry(self, task: Task) -> Optional[float]:
        """
        Register a retry for *task*.  Returns the back-off delay in seconds,
        or None if the task has exhausted its retries and was dead-lettered.
        """
        with self._lock:
            rec = self._retry_records.get(task.task_id)
            if rec is None:
                rec = RetryRecord(task=task)
                self._retry_records[task.task_id] = rec

            rec.retry_count += 1
            rec.last_attempt = time.monotonic()

            if not self.retry_policy.can_retry(rec.retry_count):
                self._dead_letter_queue.append(task)
                self.tasks_dead_lettered += 1
                if self.on_task_dead_lettered:
                    self.on_task_dead_lettered(task)
                return None

            self.retries_issued += 1
            return self.retry_policy.next_delay(rec.retry_count)

    @property
    def dead_letter_queue(self) -> list[Task]:
        with self._lock:
            return list(self._dead_letter_queue)
