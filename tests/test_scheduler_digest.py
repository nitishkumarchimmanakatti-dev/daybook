"""Tests for Daybook scheduler and daily digest flow."""

from datetime import date, time
from pathlib import Path
import pytest
import yaml

from scheduler import run_daily_digest
from approvals import load_pending_items, approve_request
from log import read_logs


def test_daily_digest_full_cycle(isolated_daybook):
    """Test full cycle: auto actions run, approval actions queued, logs written."""
    tasks_file = isolated_daybook["tasks_file"]
    journal_file = isolated_daybook["journal"]
    pending_file = isolated_daybook["pending"]
    log_file = isolated_daybook["log"]

    tasks_data = [
        # 1. Delegable, safe, no approval needed -> runs immediately
        {
            "id": "auto-note",
            "title": "Log Morning Notes",
            "schedule": {"type": "daily"},
            "due_time": "08:00",
            "mode": "delegate",
            "action": {
                "name": "log_note",
                "text": "Daily cycle check",
            },
            "status": "open",
            "requires_approval": False,
        },
        # 2. Delegable, data modifying -> requires approval -> queues in pending.md
        {
            "id": "data-folder",
            "title": "Create Folder",
            "schedule": {"type": "daily"},
            "due_time": "08:00",
            "mode": "delegate",
            "action": {
                "name": "create_folder",
                "folder": "daily_reports",
            },
            "status": "open",
            "requires_approval": True,
        },
        # 3. Remind only -> logged as NOTIFIED
        {
            "id": "team-sync",
            "title": "Join team sync",
            "schedule": {"type": "daily"},
            "due_time": "10:00",
            "mode": "remind",
            "status": "open",
        },
    ]
    tasks_file.write_text(yaml.safe_dump(tasks_data), encoding="utf-8")

    # Run digest
    digest = run_daily_digest(notify=False, today_override=date.today())

    assert len(digest["due_tasks"]) == 3

    # 1. auto-note should have executed
    assert journal_file.exists()
    assert "Daily cycle check" in journal_file.read_text(encoding="utf-8")

    # 2. data-folder should be in pending.md
    pending = load_pending_items(pending_file)
    assert len(pending) == 1
    assert pending[0].task_id == "data-folder"
    assert pending[0].status == "PENDING"

    # 3. Check daybook_log.csv has all rows
    logs = read_logs(log_file)
    task_ids_logged = {l["task_id"] for l in logs}
    assert "auto-note" in task_ids_logged
    assert "data-folder" in task_ids_logged
    assert "team-sync" in task_ids_logged


def test_daily_digest_dry_run_leaves_state_untouched(isolated_daybook):
    """Test dry_run flag in daily digest makes no file or pending modifications."""
    tasks_file = isolated_daybook["tasks_file"]
    journal_file = isolated_daybook["journal"]
    pending_file = isolated_daybook["pending"]
    log_file = isolated_daybook["log"]

    tasks_data = [
        {
            "id": "dry-note",
            "title": "Dry Note",
            "schedule": {"type": "daily"},
            "due_time": "08:00",
            "mode": "delegate",
            "action": "log_note",
            "status": "open",
            "requires_approval": False,
        }
    ]
    tasks_file.write_text(yaml.safe_dump(tasks_data), encoding="utf-8")

    digest = run_daily_digest(dry_run=True, notify=False, today_override=date.today())

    assert not journal_file.exists()
    assert not pending_file.exists()
    assert not log_file.exists()
    assert len(digest["due_tasks"]) == 1
    assert any("[DRY RUN]" in a["result"] for a in digest["executed_actions"])
