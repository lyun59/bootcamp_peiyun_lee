# Homework 06 — Stage 06: Data Preprocessing

Cleans the sample raw dataset using reusable functions in `src/cleaning.py`.

## Cleaning strategy

1. **Impute missing numeric values with the median** (`fill_missing_median`)
   for `age`, `income`, `score`. Median is robust to outliers, so it beats the
   mean for skewed data like income.
2. **Drop high-missing columns** (`drop_missing`, threshold 0.5). `extra_data`
   is 71% missing (5 of 7 rows), so it is removed rather than imputed.
3. **Min-max scale numeric columns** (`normalize_data`) so `age`, `income`,
   `score` share a [0, 1] range before modeling.

## Assumptions

- Median is the right single-value imputation for these numeric columns.
- A column missing more than half its values carries too little signal to keep.
- Min-max scaling is preferred over z-score here (bounded [0, 1], preserves shape).

## Not addressed (future work)

- `city` mixes `SF` and `San Francisco` for the same place and contains
  `Unknown` — needs categorical cleanup / encoding in a later stage.

## Files

- `src/cleaning.py` — the three reusable functions with docstrings.
- `stage06_data-preprocessing_homework-starter.ipynb` — applies them and compares.
- `data/raw/sample_data.csv` — raw input.
- `data/processed/sample_data_cleaned.csv` — cleaned output.
