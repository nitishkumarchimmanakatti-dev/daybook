"""Tests for Approvals module and pending.md handling.

Covers:
- Adding items to pending.md
- Approving items and executing actions
- Denying items
- Denied items not being retried
- Approval requirement logic
"""

from pathlib import Path
import pytest

from approvals import (
    load_pending_items,
    save_pending_items,
    add_pending_request,
    approve_request,
    deny_request,
    PendingApproval,
)
from actions import get_action
from log import read_logs


def test_add_and_load_pending(isolated_daybook):
    """Test adding items to pending.md and parsing them back."""
    pending_file = isolated_daybook["pending"]

    item = add_pending_request(
        task_id="move-1",
        title="Move downloaded invoice",
        action="move_file",
        params={"filename": "invoice.pdf"},
        reason="Requires approval to move files",
        pending_file=pending_file,
    )
    assert item.id == "move-1"
    assert item.status == "PENDING"
    assert pending_file.exists()

    loaded = load_pending_items(pending_file)
    assert len(loaded) == 1
    assert loaded[0].id == "move-1"
    assert loaded[0].title == "Move downloaded invoice"
    assert loaded[0].action == "move_file"
    assert loaded[0].params == {"filename": "invoice.pdf"}


def test_approve_request_executes_action(isolated_daybook):
    """Test approving a pending request executes the action and updates status."""
    downloads_dir = isolated_daybook["downloads"]
    archive_dir = isolated_daybook["archive"]
    pending_file = isolated_daybook["pending"]

    # Place source file in Downloads
    src = downloads_dir / "invoice.pdf"
    src.write_text("dummy invoice data", encoding="utf-8")

    # Add to pending
    add_pending_request(
        task_id="move-inv",
        title="Move invoice",
        action="move_file",
        params={"filename": "invoice.pdf"},
        reason="File move requires user sign-off",
        pending_file=pending_file,
    )

    # Approve request
    success, msg = approve_request("move-inv", pending_file=pending_file)
    assert success is True
    assert "Moved file invoice.pdf" in msg

    # Verify file moved
    assert not src.exists()
    assert (archive_dir / "invoice.pdf").exists()

    # Verify status in pending.md is EXECUTED
    loaded = load_pending_items(pending_file)
    assert len(loaded) == 1
    assert loaded[0].status == "EXECUTED"

    # Verify log entry has approved_by: user
    logs = read_logs(isolated_daybook["log"])
    executed_log = next(l for l in logs if l["task_id"] == "move-inv" and l["approved_by"] == "user")
    assert "Moved file" in executed_log["result"]


def test_deny_request_marks_denied(isolated_daybook):
    """Test denying a request marks it as DENIED and logs decision."""
    pending_file = isolated_daybook["pending"]

    add_pending_request(
        task_id="create-fld",
        title="Create temporary folder",
        action="create_folder",
        params={"folder": "tmp_work"},
        reason="Needs approval",
        pending_file=pending_file,
    )

    success, msg = deny_request("create-fld", pending_file=pending_file)
    assert success is True
    assert "Denied request 'create-fld'" in msg

    loaded = load_pending_items(pending_file)
    assert loaded[0].status == "DENIED"

    # Verify cannot re-deny or re-approve an already DENIED request
    success_retry, err_msg = approve_request("create-fld", pending_file=pending_file)
    assert success_retry is False
    assert "already DENIED" in err_msg


def test_approval_permission_rules():
    """Verify the strict rule:
    Every action that modifies data requires approval unless:
    requires_approval is false AND action is log_note or draft_message.
    """
    log_act = get_action("log_note", {"text": "Note"})
    draft_act = get_action("draft_message", {"subject": "Hi"})
    folder_act = get_action("create_folder", {"folder": "fld"})
    move_act = get_action("move_file", {"filename": "f.txt"})
    delete_act = get_action("delete_file", {"filename": "f.txt"})

    # Case 1: requires_approval: false
    assert log_act.can_auto_execute(requires_approval=False) is True
    assert draft_act.can_auto_execute(requires_approval=False) is True
    assert folder_act.can_auto_execute(requires_approval=False) is False
    assert move_act.can_auto_execute(requires_approval=False) is False
    assert delete_act.can_auto_execute(requires_approval=False) is False

    # Case 2: requires_approval: true
    assert log_act.can_auto_execute(requires_approval=True) is False
    assert draft_act.can_auto_execute(requires_approval=True) is False
    assert folder_act.can_auto_execute(requires_approval=True) is False
    assert move_act.can_auto_execute(requires_approval=True) is False
    assert delete_act.can_auto_execute(requires_approval=True) is False
