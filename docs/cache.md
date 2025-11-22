# Translation cache and cleanup

BabelDOC stores translation results in a SQLite database at `~/.cache/babeldoc/cache.v1.db` by default, using the `CACHE_FOLDER` constant defined in `babeldoc/const.py`. The file is created on startup together with other caches such as `tiktoken` assets under the same folder.

## How cleanup works

`TranslationCache` randomly triggers a cleanup when cache entries are read or written. The cleanup routine keeps only the newest 50,000 rows by deleting older entries based on their auto-incrementing `id`, and a mutex prevents multiple threads from cleaning at the same time. This helps keep the cache responsive without adding latency to every request.

### Recommended maintenance

- Occasional users: rely on the automatic cleanup; no extra steps are needed.
- Heavy translation workloads: consider removing `cache.v1.db` weekly or monthly during downtime if disk usage grows, or rotate the parent cache directory as part of housekeeping scripts.

## Quick start

```bash
# Redirect cache storage to a temporary location for a single run
HOME=/tmp/babeldoc-cache-demo babeldoc --files your.pdf --openai --ignore-cache

# Skip cached translations without deleting the database
babeldoc --files your.pdf --openai --ignore-cache

# Manually clear the translation cache (also removes WAL/SHM files if present)
rm -f ~/.cache/babeldoc/cache.v1.db ~/.cache/babeldoc/cache.v1.db-*
```

The cache path follows `HOME` (as seen in `CACHE_FOLDER`), so changing `HOME` or symlinking `~/.cache/babeldoc` lets you relocate the database. Use `--ignore-cache` when you want to bypass stored translations for a run.
