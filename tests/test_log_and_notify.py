"""Tests for log.py and notify.py."""

from pathlib import Path
from datetime import datetime
import pytest

from log import log_entry, read_logs, LOG_FIELDS
from notify import send_macos_notification, print_digest
from tasks import Task
from approvals import PendingApproval


def test_log_file_creation_and_reading(isolated_daybook):
    """Test daybook_log.csv structure, headers, and appending."""
    log_file = isolated_daybook["log"]

    log_entry(
        task_id="task-1",
        action="log_note",
        result="Success",
        approved_by="system",
        log_path=log_file,
    )
    log_entry(
        task_id="task-2",
        action="move_file",
        result="Moved file",
        approved_by="user",
        log_path=log_file,
    )

    rows = read_logs(log_file)
    assert len(rows) == 2
    assert rows[0]["task_id"] == "task-1"
    assert rows[0]["action"] == "log_note"
    assert rows[0]["result"] == "Success"
    assert rows[0]["approved_by"] == "system"

    assert rows[1]["task_id"] == "task-2"
    assert rows[1]["approved_by"] == "user"


def test_notify_mac_and_terminal(capsys):
    """Test macOS notification helper and terminal digest printer."""
    # macOS notification should not raise error regardless of environment
    result = send_macos_notification("Title", "Message", "Subtitle")
    assert isinstance(result, bool)

    # Terminal output check
    t = Task(id="t1", title="Task Title", due_time="08:00", mode="remind")
    p = PendingApproval(
        id="p1",
        task_id="t1",
        title="Pending Task",
        action="create_folder",
        params={},
        reason="Approval needed",
        requested_at="2026-11-04 08:00:00",
    )

    print_digest(
        due_tasks=[t],
        overdue_tasks=[],
        pending_items=[p],
        executed_actions=[{"task_id": "t1", "action": "log_note", "result": "Done"}],
    )

    captured = capsys.readouterr()
    assert "DAYBOOK DAILY DIGEST" in captured.out
    assert "TASKS DUE TODAY (1)" in captured.out
    assert "ITEMS AWAITING APPROVAL (1)" in captured.out
    assert "ACTIONS PROCESSED (1)" in captured.out
