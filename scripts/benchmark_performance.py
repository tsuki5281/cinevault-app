"""Read-only performance benchmark for the CineVault database layer.

Run from the repository root with the project's virtual environment active:
    python scripts/benchmark_performance.py

The benchmark measures backend function execution, not full Streamlit page
rendering. It does not insert, update, or delete any database records.
"""

from __future__ import annotations

import csv
import math
import os
import platform
import statistics
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Callable, Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from db.catalogue import (  # noqa: E402
    browse_movies,
    get_movie_details,
    get_search_suggestions,
)
from db.mariadb import get_highest_rated_movies  # noqa: E402
from db.mongodb import (  # noqa: E402
    get_most_reviewed_movies,
    get_movie_reviews,
    get_popular_tags,
)


WARMUP_REQUESTS = 5
SEQUENTIAL_REQUESTS = 30
CONCURRENT_REQUESTS = 50
WORKER_LEVELS = (1, 5, 10)


# Read-only operations representative of CineVault's main database features.
OPERATIONS: dict[str, Callable[[], Any]] = {
    "movie_title_search": lambda: browse_movies(
        title="3 Idiots",
        limit=20,
        offset=0,
    ),
    "actor_genre_filter": lambda: browse_movies(
        genres=["Horror Movies", "Thrillers"],
        actors=["Rajneesh Duggal", "Adah Sharma"],
        genre_match="all",
        actor_match="all",
        sort_by="title_asc",
        limit=20,
        offset=0,
    ),
    "movie_details": lambda: get_movie_details("s10"),
    "search_suggestions": lambda: get_search_suggestions(
        "Rajneesh",
        limit=5,
    ),
    "highest_rated_movies": lambda: get_highest_rated_movies(
        minimum_ratings=2,
        limit=10,
    ),
    "most_reviewed_movies": lambda: get_most_reviewed_movies(
        limit=10,
    ),
    "community_reviews": lambda: get_movie_reviews(
        "s101",
        hide_spoilers=True,
        limit=50,
    ),
    "popular_review_tags": lambda: get_popular_tags(10),
}


def percentile(values: list[float], fraction: float) -> float | None:
    """Return nearest-rank percentile in milliseconds."""
    if not values:
        return None
    ordered = sorted(values)
    index = max(0, math.ceil(fraction * len(ordered)) - 1)
    return ordered[index]


def summarize(
    test_name: str,
    operation: str,
    latencies_ms: list[float],
    failures: list[str],
    workers: int,
    total_elapsed_s: float,
) -> dict[str, Any]:
    successes = len(latencies_ms)
    requests = successes + len(failures)
    throughput = successes / total_elapsed_s if total_elapsed_s > 0 else 0.0

    return {
        "test": test_name,
        "operation": operation,
        "requests": requests,
        "successes": successes,
        "failures": len(failures),
        "workers": workers,
        "total_elapsed_seconds": round(total_elapsed_s, 6),
        "throughput_ops_per_sec": round(throughput, 3),
        "average_ms": round(statistics.mean(latencies_ms), 3) if latencies_ms else None,
        "median_ms": round(statistics.median(latencies_ms), 3) if latencies_ms else None,
        "p95_ms": round(percentile(latencies_ms, 0.95), 3) if latencies_ms else None,
        "min_ms": round(min(latencies_ms), 3) if latencies_ms else None,
        "max_ms": round(max(latencies_ms), 3) if latencies_ms else None,
        "error_examples": " | ".join(failures[:3]),
    }


def call_and_time(operation: Callable[[], Any]) -> tuple[float | None, str | None]:
    start = time.perf_counter()
    try:
        operation()
        elapsed_ms = (time.perf_counter() - start) * 1000
        return elapsed_ms, None
    except Exception as exc:  # Keep the rest of the benchmark running.
        elapsed_ms = (time.perf_counter() - start) * 1000
        return elapsed_ms, f"{type(exc).__name__}: {exc}"


def run_sequential(operation_name: str, operation: Callable[[], Any]) -> dict[str, Any]:
    print(f"\n[Sequential] {operation_name}: warming up ({WARMUP_REQUESTS} requests)")
    warmup_errors: list[str] = []
    for _ in range(WARMUP_REQUESTS):
        _, error = call_and_time(operation)
        if error:
            warmup_errors.append(error)

    print(f"[Sequential] {operation_name}: measuring ({SEQUENTIAL_REQUESTS} requests)")
    latencies: list[float] = []
    failures: list[str] = []
    total_start = time.perf_counter()

    for _ in range(SEQUENTIAL_REQUESTS):
        elapsed_ms, error = call_and_time(operation)
        if error:
            failures.append(error)
        elif elapsed_ms is not None:
            latencies.append(elapsed_ms)

    total_elapsed = time.perf_counter() - total_start
    summary = summarize(
        "sequential",
        operation_name,
        latencies,
        failures + warmup_errors,
        1,
        total_elapsed,
    )
    summary["requests"] = SEQUENTIAL_REQUESTS
    summary["failures"] = len(failures)
    summary["successes"] = SEQUENTIAL_REQUESTS - len(failures)
    summary["error_examples"] = " | ".join((failures + warmup_errors)[:3])
    return summary


def run_concurrent(
    operation_name: str,
    operation: Callable[[], Any],
    workers: int,
) -> dict[str, Any]:
    print(
        f"[Concurrent] {operation_name}: {CONCURRENT_REQUESTS} requests "
        f"with {workers} worker(s)"
    )
    latencies: list[float] = []
    failures: list[str] = []
    total_start = time.perf_counter()

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [
            executor.submit(call_and_time, operation)
            for _ in range(CONCURRENT_REQUESTS)
        ]
        for future in as_completed(futures):
            elapsed_ms, error = future.result()
            if error:
                failures.append(error)
            elif elapsed_ms is not None:
                latencies.append(elapsed_ms)

    total_elapsed = time.perf_counter() - total_start
    return summarize(
        f"concurrent_{workers}_workers",
        operation_name,
        latencies,
        failures,
        workers,
        total_elapsed,
    )


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    fieldnames = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    output_dir = PROJECT_ROOT / "performance_results"
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 72)
    print("CINEVAULT DATABASE PERFORMANCE BENCHMARK")
    print("=" * 72)
    print(f"Timestamp: {datetime.now().astimezone().isoformat(timespec='seconds')}")
    print(f"Python: {sys.version.split()[0]}")
    print(f"Platform: {platform.platform()}")
    print(f"Logical CPU count: {os.cpu_count()}")
    print("Mode: read-only database operations; no records will be modified.")
    print(f"Output folder: {output_dir}")

    sequential_rows: list[dict[str, Any]] = []
    concurrent_rows: list[dict[str, Any]] = []

    for operation_name, operation in OPERATIONS.items():
        try:
            sequential_rows.append(run_sequential(operation_name, operation))
        except Exception as exc:
            print(f"ERROR benchmarking {operation_name}: {type(exc).__name__}: {exc}")

    for operation_name, operation in OPERATIONS.items():
        for workers in WORKER_LEVELS:
            try:
                concurrent_rows.append(
                    run_concurrent(operation_name, operation, workers)
                )
            except Exception as exc:
                print(
                    f"ERROR concurrency test for {operation_name} "
                    f"({workers} workers): {type(exc).__name__}: {exc}"
                )

    sequential_path = output_dir / "sequential_results.csv"
    concurrent_path = output_dir / "concurrency_results.csv"
    write_csv(sequential_path, sequential_rows)
    write_csv(concurrent_path, concurrent_rows)

    print("\n" + "=" * 72)
    print("BENCHMARK SUMMARY")
    print("=" * 72)
    print("Sequential results (average ms / P95 ms / ops per second):")
    for row in sequential_rows:
        print(
            f"  {row['operation']:<24} "
            f"avg={str(row['average_ms']):>9}  "
            f"p95={str(row['p95_ms']):>9}  "
            f"throughput={row['throughput_ops_per_sec']:>8}  "
            f"failures={row['failures']}"
        )

    print("\nConcurrency results (average ms / ops per second / failures):")
    for row in concurrent_rows:
        print(
            f"  {row['operation']:<24} "
            f"{row['workers']:>2} worker(s)  "
            f"avg={str(row['average_ms']):>9}  "
            f"throughput={row['throughput_ops_per_sec']:>8}  "
            f"failures={row['failures']}"
        )

    print("\nCSV files saved:")
    print(f"  {sequential_path}")
    print(f"  {concurrent_path}")

    if not sequential_rows and not concurrent_rows:
        print("No benchmark data was collected. Check the database connections and imports.")
        return 1

    total_failures = sum(row["failures"] for row in sequential_rows + concurrent_rows)
    if total_failures:
        print(
            f"\nCompleted with {total_failures} recorded failure(s). "
            "Review error_examples in the CSV files before interpreting results."
        )
    else:
        print("\nAll benchmark requests completed successfully.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
