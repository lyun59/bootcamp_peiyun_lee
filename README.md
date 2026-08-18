# Bootcamp Repository

## Folder Structure
- **homework/** -> All homework contributions will be submitted here.
- **project/** -> All project contributions will be submitted here.
- **class_materials/** -> Local storage for class materials. Never pushed to GitHub.

## Homework Folder Rules
- Each homework will be in its own subfolder (`homework0`, `homework1`, etc.)
- Include all required files for grading.

## Project Folder Rules
- Keep project files organized and clearly named.

## Data Storage

Each homework that ingests or transforms data follows the same storage convention:

- **`data/raw/`** — unmodified, as-ingested data (e.g. `*.csv` from an API or scrape).
- **`data/processed/`** — cleaned/transformed outputs (e.g. `*.parquet`, summary files).

### Formats
- **CSV** — human-readable and portable; used for raw ingest and easy inspection.
- **Parquet** — columnar binary format; smaller and faster, and preserves dtypes; used for the processed layer. Requires `pyarrow` (or `fastparquet`).

### Environment-driven paths
Storage paths are read from `.env` so the same code works across machines without edits:

```
DATA_DIR_RAW=data/raw
DATA_DIR_PROCESSED=data/processed
```

The notebook reads them via `os.getenv('DATA_DIR_RAW', 'data/raw')` and `os.getenv('DATA_DIR_PROCESSED', 'data/processed')` (those strings are the fallback defaults). `.env` is git-ignored; `.env.example` is committed as the template.

### IO utilities
`write_df(df, path)` and `read_df(path)` route by file suffix (`.csv` → CSV, `.parquet`/`.pq` → Parquet), create parent directories as needed, and raise a clear error if the Parquet engine is missing.

## Data Preprocessing

Cleaning is done with reusable functions in `homework/homework6/src/cleaning.py`:

- **`fill_missing_median(df, columns)`** — impute NaNs with the column median (robust to outliers).
- **`drop_missing(df, threshold=0.5)`** — drop columns missing more than `threshold` of their values.
- **`normalize_data(df, columns)`** — min-max scale numeric columns to `[0, 1]`.

Each returns a new DataFrame (never mutates the input), so steps can be chained and the raw data stays available for before/after comparison.
