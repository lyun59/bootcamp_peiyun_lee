# Homework 02 — Stage 02: Tooling Setup

Sets up the project scaffold and configuration helpers used throughout the bootcamp.

## What this stage does
- **Environment**: Python via miniforge3 (see `requirements.txt`).
- **Project structure**: `data/raw/`, `data/processed/`, `notebooks/`, `src/`, `docs/`, `reports/`, `model/`.
- **Secrets**: `.env` (git-ignored) holds `API_KEY` and `DATA_DIR`; `.env.example` is the committed template.
- **Config helper**: `src/config.py` exposes `get_key()` plus `PROJECT_ROOT` / `DATA_DIR`.
- **Notebook**: `notebooks/00_project_setup.ipynb` verifies the environment and runs a NumPy demo.

## How to use
1. `cp .env.example .env` (fill real values when a real key is needed).
2. Run `notebooks/00_project_setup.ipynb` to verify the environment.
3. Import `src.config` in other scripts for env-driven config.
