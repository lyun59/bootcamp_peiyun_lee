"""Project-wide configuration and path helpers (Stage 02 — Tooling Setup).

All paths are resolved relative to the project root (the ``project/`` folder),
so notebooks and scripts work no matter which directory they are launched from.
"""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# project/src/config.py -> project/
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Load project/.env (git-ignored) if it exists.
load_dotenv(PROJECT_ROOT / ".env")


def get(key: str, default: Optional[str] = None) -> Optional[str]:
    """Return the value of an environment variable, or ``default``."""
    return os.getenv(key, default)


# --- Project-specific settings (edit in .env, not here) ---
TICKER = get("TICKER", "TSM")
START = get("START", "2020-01-01")
END = get("END", "2025-12-31")

# Storage paths, resolved against the project root.
DATA_DIR_RAW = PROJECT_ROOT / (get("DATA_DIR_RAW", "data/raw") or "data/raw")
DATA_DIR_PROCESSED = PROJECT_ROOT / (
    get("DATA_DIR_PROCESSED", "data/processed") or "data/processed"
)
