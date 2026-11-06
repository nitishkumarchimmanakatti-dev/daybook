"""Tests for Daybook CLI entry point (main.py).

Covers:
- digest command
- pending command
- approve command
- deny command
- done command
- --dry-run flag
"""

import subprocess
import sys
from pathlib import Path
import pytest
import yaml

from approvals import add_pending_request


def run_cli(*args: str, cwd: Path) -> subprocess.CompletedProcess:
    """Helper to run main.py via subprocess."""
    main_py = Path(__file__).parent.parent / "main.py"
    return subprocess.run(
        [sys.executable, str(main_py), *args],
        cwd=str(cwd),
        capture_output=True,
        text=True,
    )


def test_cli_digest_and_dry_run(isolated_daybook):
    """Test `python main.py digest` and `--dry-run`."""
    tasks_file = isolated_daybook["tasks_file"]
    journal_file = isolated_daybook["journal"]

    task_data = [
        {
            "id": "cli-journal",
            "title": "Daily Reflection",
            "schedule": {"type": "daily"},
            "due_time": "08:00",
            "mode": "delegate",
            "action": {
                "name": "log_note",
                "text": "CLI test entry",
            },
            "status": "open",
            "requires_approval": False,
        }
    ]
    tasks_file.write_text(yaml.safe_dump(task_data), encoding="utf-8")

    # 1. Test with --dry-run: journal file should NOT be created
    res_dry = run_cli("digest", "--dry-run", cwd=isolated_daybook["root"])
    assert res_dry.returncode == 0
    assert "DAYBOOK DAILY DIGEST" in res_dry.stdout
    assert not journal_file.exists()

    # 2. Test without --dry-run: journal file should be created
    res_real = run_cli("digest", cwd=isolated_daybook["root"])
    assert res_real.returncode == 0
    assert "DAYBOOK DAILY DIGEST" in res_real.stdout
    assert journal_file.exists()
    assert "CLI test entry" in journal_file.read_text(encoding="utf-8")


def test_cli_pending_and_approve_and_deny(isolated_daybook):
    """Test `python main.py pending`, `approve`, and `deny`."""
    pending_file = isolated_daybook["pending"]

    # Seed pending.md
    add_pending_request(
        task_id="req-1",
        title="Sample Approval Task",
        action="log_note",
        params={"text": "Approved Note"},
        reason="Testing approval CLI",
        pending_file=pending_file,
    )

    # 1. python main.py pending
    res_pending = run_cli("pending", cwd=isolated_daybook["root"])
    assert res_pending.returncode == 0
    assert "req-1" in res_pending.stdout
    assert "Sample Approval Task" in res_pending.stdout

    # 2. python main.py approve req-1
    res_appr = run_cli("approve", "req-1", cwd=isolated_daybook["root"])
    assert res_appr.returncode == 0
    assert "Appended note" in res_appr.stdout

    # 3. Add second request and deny it
    add_pending_request(
        task_id="req-2",
        title="Deny Test",
        action="create_folder",
        params={"folder": "test_folder"},
        reason="Testing deny CLI",
        pending_file=pending_file,
    )
    res_deny = run_cli("deny", "req-2", cwd=isolated_daybook["root"])
    assert res_deny.returncode == 0
    assert "Denied request 'req-2'" in res_deny.stdout


def test_cli_done(isolated_daybook):
    """Test `python main.py done <id>`."""
    tasks_file = isolated_daybook["tasks_file"]
    task_data = [
        {
            "id": "todo-task",
            "title": "Do something",
            "schedule": {"type": "daily"},
            "due_time": "10:00",
            "mode": "remind",
            "status": "open",
        }
    ]
    tasks_file.write_text(yaml.safe_dump(task_data), encoding="utf-8")

    res = run_cli("done", "todo-task", cwd=isolated_daybook["root"])
    assert res.returncode == 0
    assert "Marked task 'todo-task' complete" in res.stdout
