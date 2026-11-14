# CineVault Performance Analysis

**Test date:** 13 November 2026  
**Application:** CineVault (Streamlit)  
**Testing type:** Local backend benchmarking and browser profiling

## 1. Objective and scope

The performance evaluation examined the responsiveness and reliability of selected CineVault database operations, how those operations behaved under simulated concurrent requests, and the browser activity observed during common page transitions.

The evaluation covered:

- Response time and throughput of selected MariaDB and MongoDB functions.
- Backend behaviour with 1, 5 and 10 worker threads.
- Successful and failed request counts.
- Browser network activity and frontend scripting, rendering and painting during navigation.

The tests were conducted locally. The concurrent tests simulate database-function calls from Python worker threads; they are not a simulation of multiple complete Streamlit browser sessions.

## 2. Test environment and methodology

### 2.1 Environment

| Component | Configuration |
|---|---|
| Application framework | Streamlit 1.67.0 |
| Operating environment | Windows local development machine |
| Relational database | Local MariaDB server |
| Document database | Local MongoDB server (Compass connection shown as `localhost:27017`) |
| Frontend profiling | Chrome Developer Tools: Network and Performance panels |
| Browser cache during Network tests | Disabled |
| Network throttling | No throttling |

The exact CPU model, RAM capacity, Python version and database server versions were not recorded with the benchmark output. The results should therefore be interpreted as measurements from the local test machine, not as a hardware-independent performance guarantee.

### 2.2 Backend benchmark configuration

The read-only script `scripts/benchmark_performance.py` called eight existing database operations:

| Database | Operation | Function and test input |
|---|---|---|
| MariaDB | Movie title search | `browse_movies(title="3 Idiots", limit=20)` |
| MariaDB | Actor and genre filtering | `browse_movies()` with Horror Movies, Thrillers, Rajneesh Duggal and Adah Sharma using `all` matching |
| MariaDB | Movie details | `get_movie_details("s10")` |
| MariaDB | Search suggestions | `get_search_suggestions("Rajneesh", limit=5)` |
| MariaDB | Highest-rated movies | `get_highest_rated_movies(minimum_ratings=2, limit=10)` |
| MongoDB | Most-reviewed movies | `get_most_reviewed_movies(limit=10)` |
| MongoDB | Community reviews | `get_movie_reviews("s101", hide_spoilers=True, limit=50)` |
| MongoDB | Popular review tags | `get_popular_tags(10)` |

Each operation was warmed up with 5 calls before the measured sequential run. Warm-up calls were not included in the result CSVs.

| Test | Requests per operation | Worker threads | Number of operations | Measured requests |
|---|---:|---:|---:|---:|
| Sequential | 30 | 1 | 8 | 240 |
| Concurrent | 50 | 1, 5 and 10 | 8 operations × 3 worker levels | 1,200 |
| **Total measured** |  |  |  | **1,440** |

For each operation, throughput was calculated as successful operations divided by the total elapsed time for that test batch. Average, median and P95 request latency were also recorded. P95 is the nearest-rank 95th percentile of the recorded request latencies.

### 2.3 Frontend profiling method

Chrome Developer Tools was used to capture four navigation transitions. For Network testing, the Network log was cleared before each transition, browser cache was disabled and throttling was set to `No throttling`. The visible Fetch and Preflight request rows were recorded.

Separate Performance traces were captured for the four transitions. The Performance panel's trace range is reported below as a recording range; it is **not** treated as a verified page-load time. The panel's scripting, rendering and painting values are included as browser profiling observations.

## 3. Backend results

### 3.1 Sequential response time and throughput

| Database | Operation | Average (ms) | Median (ms) | P95 (ms) | Throughput (ops/s) |
|---|---|---:|---:|---:|---:|
| MariaDB | Movie title search | 28.387 | 27.282 | 38.604 | 35.225 |
| MariaDB | Actor and genre filter | 32.680 | 28.577 | 49.474 | 30.598 |
| MariaDB | Movie details | 29.736 | 26.885 | 49.911 | 33.627 |
| MariaDB | Search suggestions | 35.092 | 32.606 | 46.974 | 28.495 |
| MariaDB | Highest-rated movies | 28.009 | 25.807 | 44.574 | 35.701 |
| MongoDB | Most-reviewed movies | 1.474 | 1.436 | 1.756 | 677.986 |
| MongoDB | Community reviews | 29.514 | 26.566 | 48.980 | 33.880 |
| MongoDB | Popular review tags | 0.724 | 0.695 | 0.908 | 1,380.472 |

**Observations:**

- The five measured MariaDB operations recorded average response times between approximately 28 and 35 ms.
- Search suggestions had the highest average response time among the measured MariaDB operations (35.092 ms).
- MongoDB's most-reviewed-movies and popular-review-tags operations returned aggregate results with average response times below 2 ms in this test.
- Community review retrieval averaged 29.514 ms. Unlike the two aggregation operations, it retrieves review documents, so these timings represent different workloads and should not be treated as a direct comparison of database-system performance.

### 3.2 Concurrent response time and throughput

Each worker-level test submitted 50 requests per operation to a Python `ThreadPoolExecutor`. The worker count limits how many calls execute at the same time. The table reports the measured average latency and batch throughput.

| Operation | Workers | Average (ms) | P95 (ms) | Throughput (ops/s) |
|---|---:|---:|---:|---:|
| Movie title search | 1 | 28.845 | 33.977 | 34.622 |
| Movie title search | 5 | 104.181 | 174.037 | 45.603 |
| Movie title search | 10 | 190.818 | 251.758 | 47.220 |
| Actor and genre filter | 1 | 27.764 | 36.814 | 35.976 |
| Actor and genre filter | 5 | 102.487 | 164.236 | 46.992 |
| Actor and genre filter | 10 | 188.520 | 258.571 | 48.067 |
| Movie details | 1 | 28.383 | 45.483 | 35.193 |
| Movie details | 5 | 101.840 | 142.664 | 47.613 |
| Movie details | 10 | 189.974 | 251.550 | 48.114 |
| Search suggestions | 1 | 34.188 | 48.144 | 29.222 |
| Search suggestions | 5 | 106.423 | 168.226 | 44.795 |
| Search suggestions | 10 | 203.838 | 270.392 | 44.988 |
| Highest-rated movies | 1 | 28.553 | 47.880 | 34.982 |
| Highest-rated movies | 5 | 100.713 | 127.066 | 48.100 |
| Highest-rated movies | 10 | 189.309 | 268.565 | 48.471 |
| Most-reviewed movies | 1 | 1.971 | 2.858 | 501.531 |
| Most-reviewed movies | 5 | 3.017 | 5.425 | 1,558.084 |
| Most-reviewed movies | 10 | 3.376 | 6.917 | 2,408.513 |
| Community reviews | 1 | 35.757 | 56.115 | 27.936 |
| Community reviews | 5 | 158.252 | 230.852 | 31.162 |
| Community reviews | 10 | 274.889 | 385.965 | 33.868 |
| Popular review tags | 1 | 0.814 | 1.060 | 1,187.917 |
| Popular review tags | 5 | 1.431 | 2.092 | 2,970.021 |
| Popular review tags | 10 | 2.258 | 4.150 | 2,672.753 |

**Observations:**

- For the MariaDB operations, throughput generally increased between 1 and 5 workers, then showed smaller gains between 5 and 10 workers. For example, movie title search increased from 45.603 to 47.220 operations per second between 5 and 10 workers.
- The higher worker counts also increased per-request latency. Movie title search average latency rose from 104.181 ms at 5 workers to 190.818 ms at 10 workers. This indicates diminishing throughput gains alongside longer individual request times under the tested concurrency levels.
- MongoDB community review retrieval showed a similar latency increase: average response time rose from 35.757 ms with 1 worker to 274.889 ms with 10 workers, while throughput increased more modestly from 27.936 to 33.868 operations per second.
- MongoDB aggregation operations completed very quickly in this dataset. Their calculated throughput is high and sensitive to small changes in elapsed time; these figures should be interpreted in the context of the small operation durations and local setup.

### 3.3 Backend reliability

All measured requests completed without exceptions in the benchmark output:

| Test group | Measured requests | Successful | Failed |
|---|---:|---:|---:|
| Sequential | 240 | 240 | 0 |
| Concurrent | 1,200 | 1,200 | 0 |
| **Total** | **1,440** | **1,440** | **0** |

This confirms that no runtime exceptions were recorded for the tested calls and conditions. The benchmark's success count is based on whether an operation raised an exception; it does not independently validate every returned value against an expected result.

## 4. Frontend results

### 4.1 Network requests

| Navigation transition | Requests | Fetch | Preflight | Data transferred | Average displayed request duration |
|---|---:|---:|---:|---:|---:|
| Login → Home | 6 | 3 | 3 | 459 B | 229.17 ms |
| Home → Search | 4 | 2 | 2 | 325 B | 230.75 ms |
| Search → Movie Details | 4 | 2 | 2 | 306 B | 230.00 ms |
| Movie Details → My Activity | 4 | 2 | 2 | 307 B | 231.00 ms |
| **Total** | **18** | **9** | **9** | **1,397 B** |  |

All 18 displayed request rows returned HTTP status `200`. The average displayed request duration was calculated as the arithmetic mean of the Time values visible in each cleared Network panel.

The displayed request durations were consistent across the four captures, at approximately 229–231 ms. These values describe the individual Fetch and Preflight rows shown in the Network panel, not the total time for the browser to render each page. The captured request list also does not represent every possible resource or all application processing.

### 4.2 Browser Performance traces

| Navigation transition | Trace range | Scripting | Rendering | Painting | INP | CLS |
|---|---:|---:|---:|---:|---:|---:|
| Login → Home | 1.505 s | 217 ms | 29 ms | 14 ms | 17 ms | 0 |
| Home → Search | 2.417 s | 192 ms | 52 ms | 33 ms | 9 ms | 0 |
| Search → Movie Details | 2.182 s | 214 ms | 62 ms | 34 ms | 8 ms | 0 |
| Movie Details → My Activity | 2.658 s | 614 ms | 102 ms | 38 ms | 14 ms | 0.03 |

`INP` is the Interaction to Next Paint value shown by DevTools for the captured trace, and `CLS` is the Cumulative Layout Shift value. Largest Contentful Paint (LCP) was unavailable (`—`) in these recordings and is therefore not reported.

**Observations:**

- The recorded INP values ranged from 8 to 17 ms. The CLS values were 0 for three transitions and 0.03 for Movie Details → My Activity.
- Movie Details → My Activity recorded the highest scripting time (614 ms) and rendering time (102 ms) among the four traces. This makes My Activity a useful candidate for further profiling because it presents several groups of user-specific information.
- The trace range is the selected recording window, not a verified page-load duration. Browser extensions were also active during the captures, which may have contributed to the recorded browser activity.

## 5. Discussion and potential improvements

The backend tests indicate that CineVault's selected read operations completed reliably under the local test conditions. Sequential MariaDB operations returned in approximately 28–35 ms on average. MongoDB's aggregate summary operations were particularly quick for the tested data, while community review retrieval showed greater latency as worker count increased.

The concurrent tests show that throughput did not increase in proportion to the number of workers. For several MariaDB operations, throughput gains became small between 5 and 10 workers while average response time rose. Community review retrieval also experienced a substantial increase in average latency. These results suggest that further concurrency may introduce waiting or resource contention in the tested local environment; they do not, on their own, identify a specific bottleneck.

The frontend traces showed low recorded INP and small CLS values. My Activity had the largest scripting and rendering durations, so it would be a reasonable starting point for future profiling.

Potential follow-up improvements include:

1. Inspect the My Activity page for repeated data lookups or unnecessary rendering work.
2. Review frequently used MariaDB queries with `EXPLAIN` and verify that relevant join and filter columns have appropriate indexes.
3. Review MongoDB query filters, indexes and returned document volume for community review retrieval.
4. Consider pagination and caching for catalogue and review data where appropriate.
5. Repeat the tests in a hosted environment with representative user sessions before making claims about production scalability.

These are recommendations for investigation. No optimisation changes were made as part of this performance evaluation, so no before-and-after improvement is claimed.

## 6. Limitations

- Testing was conducted on one local Windows development machine using local database services.
- CPU model, RAM capacity, Python version and database server versions were not recorded alongside the result files.
- The concurrency test used Python worker threads to call database functions. It did not simulate multiple complete Streamlit browser sessions or remote users.
- Browser profiling was performed in one local browser environment. Extensions may have influenced the traces.
- The Network panel measurements cover the visible Fetch and Preflight requests captured for each transition; they are not complete page-load measurements.
- The Performance panel did not provide LCP values for these captures. Trace ranges should not be interpreted as page-load times.
- The benchmark covered eight selected read operations, not every CineVault feature or write operation.

## 7. Reproducibility and evidence

The benchmark can be reproduced from the project root with the virtual environment activated and both local database services running:

```powershell
python scripts\benchmark_performance.py
```

The script performs read-only operations and writes the measured outputs to `performance_results/`:

- `performance_results/sequential_results.csv`
- `performance_results/concurrency_results.csv`

The benchmark implementation is `scripts/benchmark_performance.py`.

# HAVENT ATTACHED 
For the frontend evidence, retain the four Chrome Network screenshots and 4 Performance screenshots in a folder such as `docs/performance_evidence/`. Filenames:

- `network_login_to_home.png`
- `network_home_to_search.png`
- `network_search_to_movie_details.png`
- `network_movie_details_to_activity.png`
- `performance_login_to_home.png`
- `performance_home_to_search.png`
- `performance_search_to_movie_details.png`
- `performance_movie_details_to_activity.png`
