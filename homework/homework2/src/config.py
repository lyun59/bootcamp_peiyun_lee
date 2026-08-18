"""Configuration helpers.

Loads environment variables from the project-level ``.env`` and exposes
``get_key`` plus resolved paths. Secrets stay out of version control.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Project root = the directory that contains ``src/`` (i.e. the homework folder).
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Load .env from the project root (not the current working directory), so this
# works no matter which folder the notebook/script is launched from.
load_dotenv(PROJECT_ROOT / ".env")


def get_key(name: str, default=None):
    """Read an environment variable with an optional fallback."""
    return os.getenv(name, default)


# Resolve the data directory from env (defaults to ./data relative to root).
DATA_DIR = (PROJECT_ROOT / get_key("DATA_DIR", "data")).resolve()
