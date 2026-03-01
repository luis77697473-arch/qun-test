"""
Worker Module — Distributed Task Processing Node
==================================================

Each Worker simulates a processing node that:
  - Accepts tasks from the Dispatcher via a thread-safe queue
  - Processes tasks with variable latency (simulating real workloads)
  - Reports processing metrics (latency, throughput) to the Monitor
  - Competes for shared resources, creating realistic contention scenarios
"""

import threading
import time
import random
import queue
from dataclasses import dataclass, field
from typing import Optional, Callable


@dataclass
class Task:
    """Represents a unit of work dispatched to a Worker."""
    task_id: int
    payload_size: float          # Simulated workload magnitude (0.0 - 1.0)
    priority: int = 0            # Higher value = higher priority
    created_at: float = field(default_factory=time.monotonic)
    required_resources: list = field(default_factory=list)  # Resource IDs needed


@dataclass
class TaskResult:
    """Result produced after a Worker processes a Task."""
    task_id: int
    worker_id: str
    latency: float               # Actual processing time in seconds
    success: bool
    error: Optional[str] = None
    completed_at: float = field(default_factory=time.monotonic)


class SharedResource:
    """
    A shared resource that Workers must acquire before processing certain tasks.
    Uses a reentrant lock to allow deadlock detection at a higher level.
    """

    def __init__(self, resource_id: str):
        self.resource_id = resource_id
        self.lock = threading.Lock()
        self.owner: Optional[str] = None

    def try_acquire(self, worker_id: str, timeout: float = 2.0) -> bool:
        acquired = self.lock.acquire(timeout=timeout)
        if acquired:
            self.owner = worker_id
        return acquired

    def release(self, worker_id: str) -> None:
        if self.owner == worker_id:
            self.owner = None
            try:
                self.lock.release()
            except RuntimeError:
                pass


class Worker:
    """
    Simulates a distributed processing node.

    Each worker runs in its own thread, pulling tasks from an internal queue,
    acquiring any required shared resources, and processing the task with
    simulated latency proportional to the payload size and a random jitter.
    """

    def __init__(
        self,
        worker_id: str,
        base_latency: float = 0.05,
        jitter: float = 0.03,
        capacity: int = 100,
        on_result: Optional[Callable[[TaskResult], None]] = None,
    ):
        self.worker_id = worker_id
        self.base_latency = base_latency
        self.jitter = jitter
        self.task_queue: queue.PriorityQueue = queue.PriorityQueue(maxsize=capacity)
        self.on_result = on_result

        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._tasks_processed = 0
        self._total_latency = 0.0
        self._lock = threading.Lock()

        # Resource registry — injected by the Dispatcher
        self._resource_registry: dict[str, SharedResource] = {}

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def start(self) -> None:
        self._running = True
        self._thread = threading.Thread(
            target=self._run_loop, name=f"worker-{self.worker_id}", daemon=True
        )
        self._thread.start()

    def stop(self) -> None:
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)

    # ------------------------------------------------------------------
    # Task submission
    # ------------------------------------------------------------------

    def submit(self, task: Task) -> bool:
        """Enqueue a task. Returns False if the queue is full."""
        try:
            # PriorityQueue sorts by first element; negate priority for max-first
            self.task_queue.put_nowait((-task.priority, task.task_id, task))
            return True
        except queue.Full:
            return False

    # ------------------------------------------------------------------
    # Processing loop
    # ------------------------------------------------------------------

    def _run_loop(self) -> None:
        while self._running:
            try:
                _, _, task = self.task_queue.get(timeout=0.1)
            except queue.Empty:
                continue
            result = self._process(task)
            with self._lock:
                self._tasks_processed += 1
                self._total_latency += result.latency
            if self.on_result:
                self.on_result(result)

    def _process(self, task: Task) -> TaskResult:
        """
        Process a single task:
          1. Acquire all required shared resources (ordered by ID to avoid deadlocks)
          2. Simulate computation
          3. Release resources
        """
        acquired_resources: list[str] = []
        start = time.monotonic()
        try:
            # Acquire resources in sorted order to reduce deadlock likelihood
            for res_id in sorted(task.required_resources):
                res = self._resource_registry.get(res_id)
                if res and not res.try_acquire(self.worker_id, timeout=2.0):
                    raise TimeoutError(
                        f"Worker {self.worker_id} timed out acquiring resource {res_id}"
                    )
                acquired_resources.append(res_id)

            # Simulate variable-latency processing
            processing_time = (
                self.base_latency
                + task.payload_size * self.base_latency * 2
                + random.uniform(-self.jitter, self.jitter)
            )
            processing_time = max(0.001, processing_time)
            time.sleep(processing_time)

            latency = time.monotonic() - start
            return TaskResult(
                task_id=task.task_id,
                worker_id=self.worker_id,
                latency=latency,
                success=True,
            )
        except TimeoutError as exc:
            latency = time.monotonic() - start
            return TaskResult(
                task_id=task.task_id,
                worker_id=self.worker_id,
                latency=latency,
                success=False,
                error=str(exc),
            )
        finally:
            for res_id in acquired_resources:
                res = self._resource_registry.get(res_id)
                if res:
                    res.release(self.worker_id)

    # ------------------------------------------------------------------
    # Metrics
    # ------------------------------------------------------------------

    @property
    def pending_tasks(self) -> int:
        return self.task_queue.qsize()

    @property
    def avg_latency(self) -> float:
        with self._lock:
            if self._tasks_processed == 0:
                return 0.0
            return self._total_latency / self._tasks_processed

    @property
    def tasks_processed(self) -> int:
        with self._lock:
            return self._tasks_processed
