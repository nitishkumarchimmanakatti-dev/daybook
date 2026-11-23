"""Logging module for Daybook.

Maintains an append-only audit trail in daybook_log.csv:
timestamp, task_id, action, result, approved_by
"""

from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path
from typing import Optional

from config import get_log_file, ensure_daybook_dirs

LOG_FIELDS = ["timestamp", "task_id", "action", "result", "approved_by"]


def log_entry(
    task_id: str,
    action: str,
    result: str,
    approved_by: str = "",
    timestamp: Optional[str] = None,
    log_path: Optional[Path] = None,
) -> None:
    """Append a structured entry to daybook_log.csv."""
    target_path = log_path or get_log_file()
    
    # Ensure parent directory exists
    target_path.parent.mkdir(parents=True, exist_ok=True)
    
    file_exists = target_path.exists()
    
    ts = timestamp or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    row = {
        "timestamp": ts,
        "task_id": task_id,
        "action": action,
        "result": result,
        "approved_by": approved_by,
    }
    
    with open(target_path, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=LOG_FIELDS)
        if not file_exists or target_path.stat().st_size == 0:
            writer.writeheader()
        writer.writerow(row)


def read_logs(log_path: Optional[Path] = None) -> list[dict[str, str]]:
    """Read all entries from daybook_log.csv."""
    target_path = log_path or get_log_file()
    if not target_path.exists():
        return []
    
    with open(target_path, mode="r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)
