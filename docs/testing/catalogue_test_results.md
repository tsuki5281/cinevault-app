# MariaDB Catalogue — Validation Results

## Import Summary

The cleaned Netflix dataset was imported into MariaDB using `scripts/import_movies.py`.

| Table | Records |
|---|---:|
| movies | 4,677 |
| genres | 20 |
| actors | 22,402 |
| movie_genres | 10,354 |
| movie_actors | 36,710 |

## Validation Results

| Validation Check | Result | Status |
|---|---:|---|
| Unique movie IDs | 4,677 | PASS |
| Incomplete movie records | 0 | PASS |
| Movies without genres | 0 | PASS |
| Movies without actors | 0 | PASS |
| Duplicate movie-genre associations | 0 | PASS |
| Duplicate movie-actor associations | 0 | PASS |
| Invalid movie-genre references | 0 | PASS |
| Invalid movie-actor references | 0 | PASS |

## Conclusion

All validation checks passed. The imported movie catalogue contains complete records, unique movie identifiers and valid genre and actor relationships.

The catalogue is ready for integration with the application's search and filtering functions.
