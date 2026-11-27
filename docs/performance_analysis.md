# CineVault Performance Analysis

**Test date:** 27 November 2026  
**Application:** CineVault (Streamlit)  
**Testing type:** Local backend benchmarking and browser profiling

## 1. Objective and Scope

The performance evaluation examined the responsiveness and reliability of selected CineVault database operations, their behaviour under simulated concurrent requests, and browser activity during common page transitions.

The evaluation covered:
- Response time and throughput of selected MariaDB and MongoDB operations.
- Backend behaviour with 1, 5 and 10 worker threads.
- MongoDB indexing performance and MariaDB versus MongoDB query performance.
- Browser network requests, scripting, rendering and painting during page navigation.
- Successful and failed request counts.

All tests were conducted locally using the updated CineVault application.

## 2. Test Environment and Methodology

### 2.1 Environment

| Component | Configuration |
|---|---|
| Operating system | Windows 11 (10.0.26300-SP0) |
| Python | 3.14.6 |
| Logical CPU count | 20 |
| Application framework | Streamlit |
| Relational database | Local MariaDB server |
| Document database | Local MongoDB server |
| Frontend profiling | Chrome Developer Tools |
| Network cache | Disabled |
| Network throttling | No throttling |

Testing was conducted on a local development machine. The exact CPU model, RAM capacity and database server versions were not recorded.

### 2.2 Backend Benchmark Configuration

The read-only script `scripts/benchmark_performance.py` measured eight database operations:

| Database | Operation | Function |
|---|---|---|
| MariaDB | Movie title search | `browse_movies()` |
| MariaDB | Actor and genre filtering | `browse_movies()` |
| MariaDB | Movie details | `get_movie_details()` |
| MariaDB | Search suggestions | `get_search_suggestions()` |
| MariaDB | Highest-rated movies | `get_highest_rated_movies()` |
| MongoDB | Most-reviewed movies | `get_most_reviewed_movies()` |
| MongoDB | Community reviews | `get_movie_reviews()` |
| MongoDB | Popular review tags | `get_popular_tags()` |

Each operation was warmed up with 5 requests before measurement.

| Test | Requests per operation | Worker threads | Total measured requests |
|---|---:|---:|---:|
| Sequential | 30 | 1 | 240 |
| Concurrent | 50 | 1, 5 and 10 | 1,200 |
| **Total** | | | **1,440** |

The benchmark recorded average response time, median, P95 latency, throughput and request failures. Throughput was calculated as successful operations divided by the total elapsed time.

### 2.3 MongoDB-Specific Tests

The script `scripts/performance_mongodb.py` conducted two additional tests, with each query timed over 200 runs.

**Test 1: Review Index Comparison**

Compared retrieving reviews using a collection scan (`COLLSCAN`) against the `movie_newest` compound index.

**Test 2: MariaDB vs MongoDB Genre Search**

Compared a three-table MariaDB JOIN against a MongoDB query using the embedded `genres` array and multikey index. Both queries retrieved movies belonging to the "Dramas" genre.

### 2.4 Frontend Profiling Method

Chrome Developer Tools was used to measure four navigation transitions:

1. Login → Home
2. Home → Search
3. Search → Movie Details
4. Movie Details → My Activity

For Network testing, the Network log was cleared before each transition, browser cache was disabled and throttling was set to No throttling. Request status, request type, transferred data and displayed request duration were recorded.

Separate Performance traces were captured for the same four transitions. Screenshots were enabled, and scripting, system, rendering and painting durations were recorded.

The Performance trace range represents the selected recording duration, not a verified page-load time.

## 3. Backend Performance Results

### 3.1 Sequential Response Time and Throughput

| Database | Operation | Average (ms) | P95 (ms) | Throughput (ops/s) |
|---|---|---:|---:|---:|
| MariaDB | Movie title search | 20.329 | 31.585 | 49.187 |
| MariaDB | Actor and genre filter | 21.564 | 37.971 | 46.368 |
| MariaDB | Movie details | 19.292 | 32.311 | 51.829 |
| MariaDB | Search suggestions | 24.721 | 38.810 | 40.449 |
| MariaDB | Highest-rated movies | 18.266 | 32.320 | 54.740 |
| MongoDB | Most-reviewed movies | 1.757 | 2.768 | 568.950 |
| MongoDB | Community reviews | 0.334 | 0.459 | 2,990.580 |
| MongoDB | Popular review tags | 0.714 | 1.007 | 1,398.191 |

**Observations:**

- The five MariaDB operations recorded average response times between 18.266 and 24.721 ms.
- Search suggestions recorded the highest average response time among the MariaDB operations.
- MongoDB aggregation operations completed in under 2 ms on average.
- Community review retrieval recorded an average response time of 0.334 ms. The query returned 4 non-spoiler reviews for movie `s101` from a collection containing 144 reviews.

### 3.2 Concurrent Response Time and Throughput

Each concurrent test submitted 50 requests per operation using Python's `ThreadPoolExecutor`.

| Operation | Workers | Average (ms) | Throughput (ops/s) |
|---|---:|---:|---:|
| Movie title search | 1 | 20.354 | 49.059 |
| Movie title search | 5 | 58.649 | 81.935 |
| Movie title search | 10 | 104.349 | 87.190 |
| Actor and genre filter | 1 | 18.379 | 54.314 |
| Actor and genre filter | 5 | 58.672 | 82.734 |
| Actor and genre filter | 10 | 102.585 | 88.520 |
| Movie details | 1 | 20.833 | 47.927 |
| Movie details | 5 | 56.129 | 84.257 |
| Movie details | 10 | 104.911 | 86.113 |
| Search suggestions | 1 | 24.760 | 40.337 |
| Search suggestions | 5 | 64.327 | 74.610 |
| Search suggestions | 10 | 112.309 | 79.442 |
| Highest-rated movies | 1 | 17.863 | 55.894 |
| Highest-rated movies | 5 | 56.238 | 85.219 |
| Highest-rated movies | 10 | 101.612 | 89.438 |
| Most-reviewed movies | 1 | 1.745 | 567.272 |
| Most-reviewed movies | 5 | 2.004 | 2,329.949 |
| Most-reviewed movies | 10 | 3.460 | 2,321.543 |
| Community reviews | 1 | 0.385 | 2,480.097 |
| Community reviews | 5 | 0.890 | 4,710.360 |
| Community reviews | 10 | 1.488 | 4,302.519 |
| Popular review tags | 1 | 0.625 | 1,560.832 |
| Popular review tags | 5 | 0.879 | 4,900.135 |
| Popular review tags | 10 | 1.596 | 4,123.881 |

**Observations:**

- MariaDB throughput generally increased when worker threads increased from 1 to 5, with smaller improvements from 5 to 10 workers.
- However, average response time also increased with more workers. For example, movie title search increased from 20.354 ms with one worker to 104.349 ms with ten workers.
- MongoDB community review retrieval also showed increasing average response time as concurrency increased, from 0.385 ms to 1.488 ms.
- MongoDB aggregation operations achieved high throughput due to their short execution times. Their throughput fluctuated at higher concurrency levels.

These results indicate that additional concurrent requests increased throughput for several operations, but also increased individual request latency.

### 3.3 Backend Reliability

All benchmark requests completed without recorded exceptions.

| Test group | Requests | Successful | Failed |
|---|---:|---:|---:|
| Sequential | 240 | 240 | 0 |
| Concurrent | 1,200 | 1,200 | 0 |
| **Total** | **1,440** | **1,440** | **0** |

The benchmark recorded a 100% success rate under the tested conditions. Success was determined by whether an operation raised an exception; returned values were not independently validated against expected results.

## 4. MongoDB-Specific Performance Results

### 4.1 Review Index Comparison

The test retrieved reviews for movie `s28` (#Alive), sorted by newest first. The collection contained 144 review documents.

| Method | Query Plan | Returned | Documents Examined | Keys Examined | Average (ms) |
|---|---|---:|---:|---:|---:|
| No index | SORT → COLLSCAN | 4 | 144 | 0 | 0.393 |
| `movie_newest` index | FETCH → IXSCAN | 4 | 4 | 4 | 0.294 |

The `movie_newest` index was approximately **1.3 times faster** in this test. It reduced the number of documents examined from 144 to 4, allowing MongoDB to retrieve the matching reviews in the required date order without performing a separate in-memory sort.

### 4.2 MariaDB vs MongoDB Genre Search

The test retrieved all movies belonging to the "Dramas" genre.

| Method | Movies Returned | Average (ms) |
|---|---:|---:|
| MariaDB: Three-table JOIN | 2,039 | 4.439 |
| MongoDB: Embedded genres array with multikey index | 2,039 | 3.341 |

Both databases returned the same 2,039 movies. MongoDB was approximately 1.33 times faster in this particular test.

The difference was small in absolute terms, and both databases were running locally. The result demonstrates the performance of these two query approaches under the tested conditions rather than proving that one database is generally faster.

## 5. Frontend Performance Results

### 5.1 Network Requests

| Navigation Transition | Requests | Fetch | Preflight | Data Transferred | Average Request Duration |
|---|---:|---:|---:|---:|---:|
| Login → Home | 6 | 3 | 3 | 497 B | 228.17 ms |
| Home → Search | 4 | 2 | 2 | 338 B | 229.00 ms |
| Search → Movie Details | 8 | 4 | 4 | 750 B | 228.88 ms |
| Movie Details → My Activity | 4 | 2 | 2 | 309 B | 230.50 ms |
| **Total** | **22** | **11** | **11** | **1,894 B** | **229.00 ms** |

An additional inline SVG data image appeared in the Search → Movie Details capture. It was not counted as an HTTP request.

All 22 displayed Fetch and Preflight requests returned HTTP status `200`.

**Observations:**

- The four navigation transitions generated 22 HTTP requests and transferred a total of 1,894 bytes.
- Average displayed request duration remained consistent at approximately 228–231 ms.
- Movie Details navigation generated more requests and transferred more data than the other transitions.
- No failed HTTP requests were observed during the captures.

The recorded request durations represent the individual Fetch and Preflight rows visible in the Network panel, not total page-loading times.

### 5.2 Browser Performance Traces

| Navigation Transition | Trace Range | Scripting | System | Rendering | Painting |
|---|---:|---:|---:|---:|---:|
| Login → Home | 2.270 s | 244 ms | 128 ms | 36 ms | 17 ms |
| Home → Search | 2.390 s | 263 ms | 134 ms | 50 ms | 29 ms |
| Search → Movie Details | 2.160 s | 221 ms | 141 ms | 76 ms | 44 ms |
| Movie Details → My Activity | 2.690 s | 548 ms | 134 ms | 79 ms | 30 ms |

**Observations:**

- Movie Details → My Activity recorded the highest scripting duration at 548 ms.
- Login → Home recorded the lowest rendering and painting durations at 36 ms and 17 ms respectively.
- Search → Movie Details recorded the highest rendering and painting durations at 76 ms and 44 ms respectively.
- The My Activity transition had the longest recorded trace range at 2.690 seconds.

These measurements represent browser activity within the selected trace ranges. They should not be interpreted as verified page-load times.

## 6. Discussion and Potential Improvements

The backend benchmark showed that all selected database operations completed successfully under the tested local conditions. MariaDB operations recorded average sequential response times between approximately 18 and 25 ms, while the tested MongoDB operations completed in under 2 ms on average.

The concurrent tests showed that increasing worker counts generally improved throughput, but also increased individual request latency. Throughput gains became smaller between 5 and 10 workers for several operations, indicating diminishing returns under the tested conditions.

The MongoDB index comparison demonstrated that the `movie_newest` index reduced the number of documents examined and improved query execution time. The MariaDB and MongoDB genre-search comparison returned identical result counts, with MongoDB recording a slightly lower average execution time in this test.

Frontend Network measurements showed consistent request durations across all four navigation transitions. Browser Performance traces highlighted My Activity as a useful area for further investigation due to its relatively high scripting duration.

Potential improvements include:

1. Investigate the My Activity page for repeated data retrieval or unnecessary rendering work.
2. Review MariaDB queries using `EXPLAIN` and verify relevant indexes.
3. Review MongoDB query filters, indexes and the amount of data retrieved.
4. Consider pagination and caching where appropriate to reduce unnecessary data retrieval.
5. Conduct further testing with larger datasets and representative concurrent user sessions.

These are suggested areas for future investigation; no performance improvement is claimed solely from these recommendations.

## 7. Limitations

- All tests were conducted on one local Windows development machine using local database services.
- CPU model, RAM capacity and database server versions were not recorded.
- Concurrent backend tests used Python worker threads calling database functions. They did not simulate multiple complete Streamlit browser sessions.
- The backend benchmark covered eight selected read operations and did not evaluate every application feature or write operation.
- The MongoDB-specific tests used a collection containing 144 reviews and should not be assumed to represent performance at larger scale.
- Browser profiling was performed in one local Chrome environment, with browser extensions active during the captures. These extensions may have influenced the results.
- Network measurements covered the visible Fetch and Preflight requests and do not represent complete page-loading times.
- Performance trace ranges represent the selected recording windows, not verified page-load times.
- INP, CLS and LCP were not recorded as part of the new frontend captures.

## 8. Reproducibility and Evidence

The backend benchmarks can be reproduced from the project root with the virtual environment activated and both local database services running.

**Main backend benchmark:**

```powershell
python scripts\benchmark_performance.py
```

**MongoDB-specific performance tests:**

```powershell
python -m scripts.performance_mongodb
```

The main benchmark generates:

- `performance_results/sequential_results.csv`
- `performance_results/concurrency_results.csv`

Frontend evidence should be retained in a folder such as `docs/performance_evidence/`:

- `network_login_to_home.png`
- `network_home_to_search.png`
- `network_search_to_movie_details.png`
- `network_movie_details_to_activity.png`
- `performance_login_to_home.png`
- `performance_home_to_search.png`
- `performance_search_to_movie_details.png`
- `performance_movie_details_to_activity.png`
