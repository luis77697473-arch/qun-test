#!/usr/bin/env python3
"""
main.py — Distributed Task Scheduler Simulation
=================================================

Orchestrates a full simulation of the predictive feedback-controlled
distributed task scheduler:

  1. Spawns N Worker nodes with heterogeneous performance profiles.
  2. Creates shared resources to simulate contention.
  3. Starts the Monitor (WMA-based scoring) and DeadlockDetector.
  4. Launches the Dispatcher and floods it with tasks.
  5. Prints a real-time dashboard and final summary report.

Usage:
    python main.py [--workers N] [--tasks M] [--resources R]
"""

import argparse
import random
import sys
import time
import threading

from scheduler.worker import Task, Worker, SharedResource
from scheduler.monitor import Monitor
from scheduler.dispatcher import Dispatcher
from scheduler.deadlock import DeadlockDetector, RetryPolicy


# ────────────────────────────────────────────────────────────────
# Configuration
# ────────────────────────────────────────────────────────────────

DEFAULT_WORKERS = 5
DEFAULT_TASKS = 200
DEFAULT_RESOURCES = 3
ALPHA = 0.6          # Speed vs stability trade-off
GAMMA = 5.0          # Trend sensitivity
MONITOR_INTERVAL = 0.15


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Distributed Task Scheduler Simulation")
    p.add_argument("--workers", type=int, default=DEFAULT_WORKERS, help="Number of workers")
    p.add_argument("--tasks", type=int, default=DEFAULT_TASKS, help="Total tasks to dispatch")
    p.add_argument("--resources", type=int, default=DEFAULT_RESOURCES, help="Number of shared resources")
    p.add_argument("--alpha", type=float, default=ALPHA, help="Speed-stability alpha")
    p.add_argument("--gamma", type=float, default=GAMMA, help="Trend sensitivity gamma")
    return p.parse_args()


# ────────────────────────────────────────────────────────────────
# Dashboard
# ────────────────────────────────────────────────────────────────

def print_dashboard(monitor: Monitor, dispatcher: Dispatcher, elapsed: float) -> None:
    snapshots = monitor.latest_snapshots
    if not snapshots:
        return

    print(f"\n{'=' * 78}")
    print(f"  LIVE DASHBOARD  |  Elapsed: {elapsed:.1f}s  |  "
          f"Dispatched: {dispatcher.total_dispatched}  "
          f"OK: {dispatcher.total_succeeded}  "
          f"Fail: {dispatcher.total_failed}")
    print(f"{'=' * 78}")
    print(f"  {'Worker':<10} {'WMA(ms)':>8} {'Vol':>7} {'Trend':>7} "
          f"{'Score':>9} {'Weight':>8} {'Pending':>8} {'Done':>6}")
    print(f"  {'-' * 72}")

    for wid in sorted(snapshots):
        s = snapshots[wid]
        print(
            f"  {s.worker_id:<10} "
            f"{s.wma_latency * 1000:>7.1f} "
            f"{s.volatility:>7.3f} "
            f"{s.trend_slope:>+7.4f} "
            f"{s.adjusted_score:>9.1f} "
            f"{s.dispatch_weight:>7.1%} "
            f"{s.pending_tasks:>8} "
            f"{s.tasks_processed:>6}"
        )
    print()


# ────────────────────────────────────────────────────────────────
# Summary
# ────────────────────────────────────────────────────────────────

def print_summary(
    dispatcher: Dispatcher,
    monitor: Monitor,
    deadlock_det: DeadlockDetector,
    elapsed: float,
) -> None:
    print("\n" + "=" * 78)
    print("  FINAL SIMULATION REPORT")
    print("=" * 78)
    print(f"  Total elapsed time     : {elapsed:.2f}s")
    print(f"  Tasks dispatched       : {dispatcher.total_dispatched}")
    print(f"  Tasks succeeded        : {dispatcher.total_succeeded}")
    print(f"  Tasks failed           : {dispatcher.total_failed}")
    print(f"  Deadlocks detected     : {deadlock_det.deadlocks_detected}")
    print(f"  Retries issued         : {deadlock_det.retries_issued}")
    print(f"  Dead-lettered tasks    : {deadlock_det.tasks_dead_lettered}")
    print()

    snapshots = monitor.latest_snapshots
    if snapshots:
        print("  Per-Worker Final Metrics:")
        print(f"  {'Worker':<10} {'Avg Lat(ms)':>12} {'Tasks Done':>11} {'Weight':>8}")
        print(f"  {'-' * 45}")
        for wid in sorted(snapshots):
            s = snapshots[wid]
            print(
                f"  {s.worker_id:<10} "
                f"{s.wma_latency * 1000:>11.2f} "
                f"{s.tasks_processed:>11} "
                f"{s.dispatch_weight:>7.1%}"
            )
    print("=" * 78)


# ────────────────────────────────────────────────────────────────
# Main simulation
# ────────────────────────────────────────────────────────────────

def run_simulation(args: argparse.Namespace) -> None:
    print(f"[*] Starting simulation: {args.workers} workers, "
          f"{args.tasks} tasks, {args.resources} shared resources\n")

    # 1. Create shared resources
    resources = [SharedResource(f"res-{i}") for i in range(args.resources)]

    # 2. Create workers with heterogeneous profiles
    workers = []
    for i in range(args.workers):
        base_lat = 0.02 + random.uniform(0.0, 0.06)   # 20-80 ms base
        jitter = random.uniform(0.005, 0.025)
        w = Worker(worker_id=f"W-{i}", base_latency=base_lat, jitter=jitter)
        workers.append(w)

    # 3. Initialise Monitor, DeadlockDetector, Dispatcher
    monitor = Monitor(alpha=args.alpha, gamma=args.gamma)
    retry_policy = RetryPolicy(base_delay=0.1, max_delay=3.0, max_retries=5)
    deadlock_det = DeadlockDetector(retry_policy=retry_policy, check_interval=0.3)
    dispatcher = Dispatcher(
        workers=workers,
        monitor=monitor,
        deadlock_detector=deadlock_det,
        shared_resources=resources,
    )

    # 4. Start all components
    for w in workers:
        w.start()
    monitor.start(interval=MONITOR_INTERVAL)
    deadlock_det.start()

    # 5. Generate and dispatch tasks in bursts (simulating high concurrency)
    start_time = time.monotonic()
    task_id = 0
    burst_size = max(1, args.tasks // 10)

    dashboard_stop = threading.Event()

    def dashboard_loop():
        while not dashboard_stop.is_set():
            elapsed = time.monotonic() - start_time
            print_dashboard(monitor, dispatcher, elapsed)
            dashboard_stop.wait(timeout=1.0)

    dash_thread = threading.Thread(target=dashboard_loop, daemon=True)
    dash_thread.start()

    remaining = args.tasks
    while remaining > 0:
        count = min(burst_size, remaining)
        batch = []
        for _ in range(count):
            # Random payload, priority, and resource requirements
            payload = random.uniform(0.1, 1.0)
            priority = random.randint(0, 5)
            # Some tasks require 0-2 shared resources
            num_res = random.randint(0, min(2, args.resources))
            required = random.sample(
                [r.resource_id for r in resources], k=num_res
            )
            batch.append(Task(
                task_id=task_id,
                payload_size=payload,
                priority=priority,
                required_resources=required,
            ))
            task_id += 1
        dispatcher.dispatch_batch(batch)
        remaining -= count
        # Small pause between bursts to let the feedback loop adapt
        time.sleep(0.05)

    # 6. Wait for workers to drain
    print("\n[*] All tasks dispatched. Waiting for workers to finish...")
    deadline = time.monotonic() + 30  # 30s hard timeout
    while time.monotonic() < deadline:
        total_pending = sum(w.pending_tasks for w in workers)
        if total_pending == 0:
            break
        time.sleep(0.2)

    # Allow last results to flow
    time.sleep(0.5)

    # 7. Stop everything
    dashboard_stop.set()
    monitor.stop()
    deadlock_det.stop()
    for w in workers:
        w.stop()

    elapsed = time.monotonic() - start_time
    print_summary(dispatcher, monitor, deadlock_det, elapsed)


# ────────────────────────────────────────────────────────────────
# Entry point
# ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    args = parse_args()
    run_simulation(args)
