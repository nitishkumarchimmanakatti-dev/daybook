"""Pytest fixtures for Daybook test suite.

Provides isolated temporary directories and environment variables
so tests never touch the user's real ~/Daybook or ~/Downloads.
"""

import os
from pathlib import Path
import pytest
import yaml

from config import ensure_daybook_dirs


@pytest.fixture(autouse=True)
def isolated_daybook(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Sets up an isolated Daybook test environment."""
    test_daybook = tmp_path / "Daybook"
    test_downloads = tmp_path / "Downloads"
    test_tasks = tmp_path / "tasks.yaml"

    test_daybook.mkdir(parents=True, exist_ok=True)
    test_downloads.mkdir(parents=True, exist_ok=True)

    monkeypatch.setenv("DAYBOOK_DIR", str(test_daybook))
    monkeypatch.setenv("DAYBOOK_DOWNLOADS_DIR", str(test_downloads))
    monkeypatch.setenv("DAYBOOK_TASKS_FILE", str(test_tasks))
    monkeypatch.setenv("DAYBOOK_DIGEST_TIME", "08:00")

    ensure_daybook_dirs()

    yield {
        "root": tmp_path,
        "daybook": test_daybook,
        "downloads": test_downloads,
        "tasks_file": test_tasks,
        "archive": test_daybook / "Archive",
        "drafts": test_daybook / "drafts",
        "journal": test_daybook / "journal.md",
        "pending": test_daybook / "pending.md",
        "log": test_daybook / "daybook_log.csv",
    }
