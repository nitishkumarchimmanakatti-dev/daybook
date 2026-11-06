"""Configuration module for Daybook.

Provides paths, defaults, and directory management with support for
environment variable overrides (useful for testing and customization).
"""

from __future__ import annotations

import os
from pathlib import Path


def get_daybook_dir() -> Path:
    """Return the base Daybook directory (~/Daybook by default)."""
    env_dir = os.environ.get("DAYBOOK_DIR")
    if env_dir:
        return Path(env_dir).expanduser().resolve()
    return (Path.home() / "Daybook").resolve()


def get_downloads_dir() -> Path:
    """Return the Downloads directory (~/Downloads by default)."""
    env_dir = os.environ.get("DAYBOOK_DOWNLOADS_DIR")
    if env_dir:
        return Path(env_dir).expanduser().resolve()
    return (Path.home() / "Downloads").resolve()


def get_tasks_file() -> Path:
    """Return the path to tasks.yaml."""
    env_path = os.environ.get("DAYBOOK_TASKS_FILE")
    if env_path:
        return Path(env_path).expanduser().resolve()
    
    local_tasks = (Path(__file__).parent / "tasks.yaml").resolve()
    if local_tasks.exists():
        return local_tasks
    
    daybook_tasks = get_daybook_dir() / "tasks.yaml"
    if daybook_tasks.exists():
        return daybook_tasks

    return local_tasks


def get_journal_file() -> Path:
    """Return the path to ~/Daybook/journal.md."""
    return get_daybook_dir() / "journal.md"


def get_archive_dir() -> Path:
    """Return the path to ~/Daybook/Archive/."""
    return get_daybook_dir() / "Archive"


def get_drafts_dir() -> Path:
    """Return the path to ~/Daybook/drafts/."""
    return get_daybook_dir() / "drafts"


def get_pending_file() -> Path:
    """Return the path to ~/Daybook/pending.md."""
    return get_daybook_dir() / "pending.md"


def get_log_file() -> Path:
    """Return the path to ~/Daybook/daybook_log.csv."""
    return get_daybook_dir() / "daybook_log.csv"


def get_digest_time() -> str:
    """Return the scheduled daily digest time in HH:MM (default 11:00)."""
    return os.environ.get("DAYBOOK_DIGEST_TIME", "11:00")


def ensure_daybook_dirs() -> None:
    """Ensure essential Daybook directories exist."""
    base = get_daybook_dir()
    base.mkdir(parents=True, exist_ok=True)
    get_archive_dir().mkdir(parents=True, exist_ok=True)
    get_drafts_dir().mkdir(parents=True, exist_ok=True)
