"""Tests for Deletion and Approval Safety Rules.

STRICT REQUIREMENTS:
- Deleting any file, note, or task is NEVER done automatically.
- When a task would delete something, the agent creates a pending approval entry
  in ~/Daybook/pending.md and does nothing else.
- Tests must prove that delete requests always create a pending approval and
  never execute on their own.
- Even if requires_approval is set to false, delete requests NEVER auto-execute.
"""

from datetime import date
from pathlib import Path
import pytest
import yaml

from actions import get_action, DeleteAction, ActionSecurityError
from approvals import load_pending_items, approve_request, deny_request
from scheduler import run_daily_digest
from log import read_logs


def test_delete_action_directly_refuses_auto_execution():
    """Prove that DeleteAction refuses auto-execution regardless of requires_approval setting."""
    action = get_action(name="delete_file", params={"filename": "important.txt"}, task_id="del-1")
    assert isinstance(action, DeleteAction)
    assert action.is_deletion is True

    # Even if requires_approval is explicitly False, can_auto_execute MUST return False
    assert action.can_auto_execute(requires_approval=False) is False
    assert action.can_auto_execute(requires_approval=True) is False

    # Direct execution attempt must strictly raise ActionSecurityError
    with pytest.raises(ActionSecurityError, match="Automatic deletion is prohibited"):
        action.execute()


def test_delete_request_in_daily_flow_creates_pending_approval_and_does_nothing_else(isolated_daybook):
    """Prove that when a task would delete something, the agent creates a pending approval entry

    in ~/Daybook/pending.md and does nothing else.
    """
    tasks_file = isolated_daybook["tasks_file"]
    pending_file = isolated_daybook["pending"]

    # Create dummy file to ensure it is NOT deleted
    target_file = isolated_daybook["daybook"] / "precious.txt"
    target_file.write_text("irreplaceable content", encoding="utf-8")

    # Configure a delegate task attempting deletion with requires_approval: false
    # to prove the strict safety override
    task_data = [
        {
            "id": "clean-old-files",
            "title": "Clean old notes and delete files",
            "notes": "Attempt to delete precious.txt",
            "schedule": {"type": "daily"},
            "due_time": "08:00",
            "mode": "delegate",
            "action": {
                "name": "delete_file",
                "filename": str(target_file),
            },
            "status": "open",
            "requires_approval": False,  # Safety override test!
        }
    ]
    tasks_file.write_text(yaml.safe_dump(task_data), encoding="utf-8")

    # Run daily digest
    result = run_daily_digest(notify=False, today_override=date.today())

    # 1. Target file MUST NOT have been deleted
    assert target_file.exists(), "Target file was deleted! Automatic deletion occurred!"
    assert target_file.read_text(encoding="utf-8") == "irreplaceable content"

    # 2. Pending approval entry MUST have been created in pending.md
    pending_items = load_pending_items(pending_file)
    assert len(pending_items) == 1
    item = pending_items[0]
    assert item.task_id == "clean-old-files"
    assert item.action == "delete_file"
    assert item.status == "PENDING"
    assert "Deletion request" in item.reason

    # 3. Executed actions summary must show awaiting approval
    assert any("Awaiting explicit approval" in a["result"] for a in result["executed_actions"])

    # 4. Daybook log must record pending approval, NOT execution
    logs = read_logs(isolated_daybook["log"])
    assert len(logs) >= 1
    del_log = next(l for l in logs if l["task_id"] == "clean-old-files")
    assert "PENDING_APPROVAL" in del_log["result"]
    assert del_log["approved_by"] == ""


def test_delete_request_denied_is_never_retried(isolated_daybook):
    """Prove that denied deletion requests are never retried without a new approval."""
    tasks_file = isolated_daybook["tasks_file"]
    pending_file = isolated_daybook["pending"]

    task_data = [
        {
            "id": "delete-task-1",
            "title": "Remove old archive task",
            "schedule": {"type": "daily"},
            "due_time": "08:00",
            "mode": "delegate",
            "action": "delete_task",
            "status": "open",
            "requires_approval": True,
        }
    ]
    tasks_file.write_text(yaml.safe_dump(task_data), encoding="utf-8")

    # 1. First run: adds to pending.md
    run_daily_digest(notify=False, today_override=date.today())
    pending_items = load_pending_items(pending_file)
    assert len(pending_items) == 1
    assert pending_items[0].status == "PENDING"

    # 2. User explicitly denies the request
    success, msg = deny_request("delete-task-1", pending_file=pending_file)
    assert success is True
    assert "Denied request" in msg

    # Verify status in pending.md is now DENIED
    pending_items = load_pending_items(pending_file)
    assert pending_items[0].status == "DENIED"

    # 3. Second run: must detect denial and NOT re-add or retry
    result = run_daily_digest(notify=False, today_override=date.today())
    actions = result["executed_actions"]
    assert any("SKIPPED (previously denied by user)" in a["result"] for a in actions)

    # pending.md should still only have the 1 DENIED item, not duplicated
    pending_items = load_pending_items(pending_file)
    assert len(pending_items) == 1
    assert pending_items[0].status == "DENIED"


def test_approved_deletion_records_user_permission(isolated_daybook):
    """Prove that explicit user approval records permission with approved_by: user."""
    tasks_file = isolated_daybook["tasks_file"]
    pending_file = isolated_daybook["pending"]

    task_data = [
        {
            "id": "delete-cache",
            "title": "Purge cache file",
            "schedule": {"type": "daily"},
            "due_time": "08:00",
            "mode": "delegate",
            "action": "delete_file",
            "status": "open",
            "requires_approval": True,
        }
    ]
    tasks_file.write_text(yaml.safe_dump(task_data), encoding="utf-8")

    # Create pending
    run_daily_digest(notify=False, today_override=date.today())

    # User approves
    success, msg = approve_request("delete-cache", pending_file=pending_file)
    assert success is True
    assert "Recorded explicit user permission" in msg

    # Verify log
    logs = read_logs(isolated_daybook["log"])
    user_log = next(l for l in logs if l["task_id"] == "delete-cache" and l["approved_by"] == "user")
    assert user_log["result"] == "APPROVED_BY_USER"
