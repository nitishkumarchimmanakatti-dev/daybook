"""Tests for Daybook Action classes.

Covers:
- LogNoteAction
- CreateFolderAction
- MoveFileAction (strict non-overwrite)
- DraftMessageAction
- Directory sandboxing and path traversal prevention
- Dry-run behavior
"""

from pathlib import Path
import pytest

from actions import (
    get_action,
    LogNoteAction,
    CreateFolderAction,
    MoveFileAction,
    DraftMessageAction,
    ActionSecurityError,
    ActionExecutionError,
)


def test_log_note_action_normal_and_dry_run(isolated_daybook):
    """Test log_note appends formatted dated entry and respects dry_run."""
    journal_file = isolated_daybook["journal"]

    action = get_action(
        name="log_note",
        params={"text": "First journal entry"},
        task_id="task-journal",
    )
    assert isinstance(action, LogNoteAction)
    assert action.can_auto_execute(requires_approval=False) is True
    assert action.can_auto_execute(requires_approval=True) is False

    # Dry-run test
    dry_action = get_action(
        name="log_note",
        params={"text": "Dry run entry"},
        task_id="task-journal",
        dry_run=True,
    )
    dry_res = dry_action.execute()
    assert "[DRY RUN]" in dry_res
    assert not journal_file.exists()

    # Real execution
    res = action.execute()
    assert journal_file.exists()
    content = journal_file.read_text(encoding="utf-8")
    assert "First journal entry" in content
    assert "Appended note" in res


def test_create_folder_sandboxing_and_traversal(isolated_daybook):
    """Test create_folder strictly enforces staying under ~/Daybook."""
    daybook_dir = isolated_daybook["daybook"]

    # 1. Valid subfolder
    action = get_action(
        name="create_folder",
        params={"folder": "projects/nov2026"},
        task_id="cf-1",
    )
    assert isinstance(action, CreateFolderAction)
    assert action.can_auto_execute(requires_approval=False) is False  # Data modifying!

    res = action.execute()
    expected_path = daybook_dir / "projects" / "nov2026"
    assert expected_path.is_dir()
    assert "Created folder" in res

    # 2. Existing folder doesn't fail
    res_repeat = action.execute()
    assert "already exists" in res_repeat

    # 3. Path traversal outside ~/Daybook must fail with ActionSecurityError
    escape_action = get_action(
        name="create_folder",
        params={"folder": "../../escape_attempt"},
        task_id="cf-escape",
    )
    with pytest.raises(ActionSecurityError, match="escapes Daybook sandbox"):
        escape_action.execute()


def test_move_file_never_overwrites(isolated_daybook):
    """Test move_file strictly enforces non-overwriting behavior."""
    downloads_dir = isolated_daybook["downloads"]
    archive_dir = isolated_daybook["archive"]

    # Source file in Downloads
    source_file = downloads_dir / "report.pdf"
    source_file.write_text("downloaded report content", encoding="utf-8")

    action = get_action(
        name="move_file",
        params={"filename": "report.pdf"},
        task_id="mv-1",
    )
    assert isinstance(action, MoveFileAction)
    assert action.can_auto_execute(requires_approval=False) is False  # Must have approval!

    # Execute move
    res = action.execute()
    assert "Moved file report.pdf" in res
    assert not source_file.exists()
    dest_file = archive_dir / "report.pdf"
    assert dest_file.exists()
    assert dest_file.read_text(encoding="utf-8") == "downloaded report content"

    # Attempt second move with a new file of same name: MUST FAIL with ActionExecutionError
    source_file_2 = downloads_dir / "report.pdf"
    source_file_2.write_text("new content", encoding="utf-8")

    repeat_action = get_action(
        name="move_file",
        params={"filename": "report.pdf"},
        task_id="mv-1",
    )
    with pytest.raises(ActionExecutionError, match="overwrite forbidden"):
        repeat_action.execute()

    # Destination still has original content
    assert dest_file.read_text(encoding="utf-8") == "downloaded report content"


def test_move_file_sandboxing(isolated_daybook):
    """Test move_file refuses source files not inside ~/Downloads."""
    # Attempt to move an arbitrary system file
    action = get_action(
        name="move_file",
        params={"filename": "/etc/hosts"},
        task_id="mv-exploit",
    )
    # The action resolves filename relative to Downloads and checks directory containment
    # If source doesn't exist in Downloads:
    with pytest.raises(ActionExecutionError, match="Source file not found in Downloads"):
        action.execute()


def test_draft_message_action(isolated_daybook):
    """Test draft_message writes a clean markdown draft to ~/Daybook/drafts/."""
    drafts_dir = isolated_daybook["drafts"]

    action = get_action(
        name="draft_message",
        params={"subject": "Project Proposal", "body": "Drafting details for client..."},
        task_id="draft-1",
    )
    assert isinstance(action, DraftMessageAction)
    assert action.can_auto_execute(requires_approval=False) is True
    assert action.can_auto_execute(requires_approval=True) is False

    res = action.execute()
    assert "Created draft message" in res

    draft_files = list(drafts_dir.glob("*.md"))
    assert len(draft_files) == 1
    content = draft_files[0].read_text(encoding="utf-8")
    assert "# Draft: Project Proposal" in content
    assert "Drafting details for client..." in content
