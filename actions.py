"""Actions module for Daybook.

Implements permitted actions with strict path resolution, sandboxing,
and permission checks. Phase 1 allowed actions:
- log_note: append dated line to ~/Daybook/journal.md
- create_folder: create directory under ~/Daybook/
- move_file: move file from ~/Downloads to ~/Daybook/Archive/ (never overwrites)
- draft_message: write markdown file to ~/Daybook/drafts/

Deletion of any file, note, or task is NEVER automatic and strictly requires
prior explicit approval.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
import os
from pathlib import Path
import re
import shutil
from typing import Any, Dict, Optional

from config import (
    get_daybook_dir,
    get_downloads_dir,
    get_journal_file,
    get_archive_dir,
    get_drafts_dir,
)


class ActionSecurityError(Exception):
    """Raised when an action violates directory sandboxing or safety rules."""
    pass


class ActionExecutionError(Exception):
    """Raised when an action fails execution (e.g., target already exists)."""
    pass


def is_path_within(target_path: Path, parent_dir: Path) -> bool:
    """Check if target_path resolves strictly within parent_dir."""
    target_resolved = target_path.resolve()
    parent_resolved = parent_dir.resolve()
    try:
        target_resolved.relative_to(parent_resolved)
        return True
    except ValueError:
        return False


class BaseAction(ABC):
    """Base class for all Daybook actions."""

    name: str = "base"
    is_deletion: bool = False

    def __init__(
        self,
        params: Optional[Dict[str, Any]] = None,
        task_id: str = "",
        task_title: str = "",
        task_notes: str = "",
        dry_run: bool = False,
    ):
        self.params = params or {}
        self.task_id = task_id
        self.task_title = task_title
        self.task_notes = task_notes
        self.dry_run = dry_run

    def can_auto_execute(self, requires_approval: bool) -> bool:
        """Approval Rule:
        Every action that modifies data requires approval unless:
        requires_approval == False AND action is log_note or draft_message.
        Deletions NEVER auto-execute under any circumstances.
        """
        if self.is_deletion:
            return False
        if requires_approval:
            return False
        return self.name in ("log_note", "draft_message")

    @abstractmethod
    def validate_safety(self) -> None:
        """Validate all parameters, paths, and boundaries before running."""
        pass

    @abstractmethod
    def execute(self) -> str:
        """Run the action safely. Returns a summary description of the outcome."""
        pass


class LogNoteAction(BaseAction):
    """Appends a dated line to ~/Daybook/journal.md."""

    name = "log_note"
    is_deletion = False

    def get_text(self) -> str:
        return (
            self.params.get("text")
            or self.params.get("content")
            or self.task_notes
            or self.task_title
            or "Daily log entry"
        )

    def validate_safety(self) -> None:
        journal_path = get_journal_file()
        daybook_dir = get_daybook_dir()
        if not is_path_within(journal_path, daybook_dir):
            raise ActionSecurityError(
                f"Journal path {journal_path} must reside strictly inside {daybook_dir}"
            )

    def execute(self) -> str:
        self.validate_safety()
        journal_path = get_journal_file()
        text = self.get_text()
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"[{ts}] {text}\n"

        if self.dry_run:
            return f"[DRY RUN] Would append to {journal_path}: {entry.strip()}"

        journal_path.parent.mkdir(parents=True, exist_ok=True)
        with open(journal_path, "a", encoding="utf-8") as f:
            f.write(entry)
        return f"Appended note to {journal_path}: '{text}'"


class CreateFolderAction(BaseAction):
    """Creates a folder under ~/Daybook/ (never outside it)."""

    name = "create_folder"
    is_deletion = False

    def get_target_path(self) -> Path:
        raw_folder = (
            self.params.get("folder")
            or self.params.get("path")
            or self.params.get("name")
            or ""
        )
        if not raw_folder:
            raise ActionExecutionError("Folder name or relative path is required.")
        
        # Strip leading slashes to prevent absolute breakout from root
        clean_folder = str(raw_folder).lstrip("/\\")
        daybook_dir = get_daybook_dir()
        target = (daybook_dir / clean_folder).resolve()
        return target

    def validate_safety(self) -> None:
        daybook_dir = get_daybook_dir()
        target = self.get_target_path()
        if not is_path_within(target, daybook_dir):
            raise ActionSecurityError(
                f"Folder {target} escapes Daybook sandbox {daybook_dir}"
            )
        if target == daybook_dir:
            raise ActionSecurityError("Cannot recreate base Daybook directory as subfolder.")

    def execute(self) -> str:
        self.validate_safety()
        target = self.get_target_path()

        if self.dry_run:
            return f"[DRY RUN] Would create directory: {target}"

        if target.exists():
            return f"Directory already exists: {target}"

        target.mkdir(parents=True, exist_ok=True)
        return f"Created folder: {target}"


class MoveFileAction(BaseAction):
    """Moves a file from ~/Downloads into ~/Daybook/Archive/ (never overwrites)."""

    name = "move_file"
    is_deletion = False

    def get_source_and_dest(self) -> tuple[Path, Path]:
        filename = (
            self.params.get("filename")
            or self.params.get("file")
            or self.params.get("source")
            or ""
        )
        if not filename:
            raise ActionExecutionError("Filename to move is required.")

        downloads_dir = get_downloads_dir()
        archive_dir = get_archive_dir()

        # Disallow directory navigation in filename
        source_name = Path(filename).name
        source_path = (downloads_dir / source_name).resolve()
        dest_path = (archive_dir / source_name).resolve()

        return source_path, dest_path

    def validate_safety(self) -> None:
        downloads_dir = get_downloads_dir()
        archive_dir = get_archive_dir()
        source_path, dest_path = self.get_source_and_dest()

        if not is_path_within(source_path, downloads_dir):
            raise ActionSecurityError(
                f"Source {source_path} must be inside Downloads directory {downloads_dir}"
            )
        if not is_path_within(dest_path, archive_dir):
            raise ActionSecurityError(
                f"Destination {dest_path} must be inside Archive directory {archive_dir}"
            )

        # Non-overwrite safety check
        if dest_path.exists():
            raise ActionExecutionError(
                f"Archive destination file already exists (overwrite forbidden): {dest_path}"
            )

    def execute(self) -> str:
        self.validate_safety()
        source_path, dest_path = self.get_source_and_dest()

        if self.dry_run:
            note = "" if source_path.exists() else " (source file not currently in Downloads)"
            return f"[DRY RUN] Would move {source_path} to {dest_path}{note}"

        if not source_path.exists():
            raise ActionExecutionError(
                f"Source file not found in Downloads: {source_path}"
            )
        if not source_path.is_file():
            raise ActionExecutionError(
                f"Source path is not a regular file: {source_path}"
            )

        dest_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source_path), str(dest_path))
        return f"Moved file {source_path.name} to {dest_path}"


class DraftMessageAction(BaseAction):
    """Writes a draft markdown file to ~/Daybook/drafts/."""

    name = "draft_message"
    is_deletion = False

    def get_subject_and_body(self) -> tuple[str, str, str]:
        subject = (
            self.params.get("subject")
            or self.params.get("title")
            or self.task_title
            or "Draft Message"
        )
        body = (
            self.params.get("body")
            or self.params.get("text")
            or self.params.get("content")
            or self.task_notes
            or ""
        )
        # Clean slug for filename
        slug = re.sub(r"[^a-zA-Z0-9_\-]+", "_", subject).strip("_").lower()
        if not slug:
            slug = "draft"
        date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{date_str}_{slug}.md"
        return subject, body, filename

    def validate_safety(self) -> None:
        drafts_dir = get_drafts_dir()
        _, _, filename = self.get_subject_and_body()
        target_path = (drafts_dir / filename).resolve()
        if not is_path_within(target_path, drafts_dir):
            raise ActionSecurityError(
                f"Draft path {target_path} must be inside {drafts_dir}"
            )

    def execute(self) -> str:
        self.validate_safety()
        drafts_dir = get_drafts_dir()
        subject, body, filename = self.get_subject_and_body()
        target_path = drafts_dir / filename

        content = (
            f"# Draft: {subject}\n"
            f"**Created**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"**Task ID**: {self.task_id}\n\n"
            f"## Message\n{body}\n"
        )

        if self.dry_run:
            return f"[DRY RUN] Would write draft to {target_path}:\n{content}"

        drafts_dir.mkdir(parents=True, exist_ok=True)
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Created draft message at {target_path}"


class DeleteAction(BaseAction):
    """Any deletion action (file, task, note).

    Deleting any file, note, or task is NEVER done automatically.
    This action has is_deletion = True and will ALWAYS require explicit user approval.
    """

    name = "delete"
    is_deletion = True

    def validate_safety(self) -> None:
        pass

    def execute(self) -> str:
        # Deletion is never executed automatically
        raise ActionSecurityError(
            "Automatic deletion is prohibited in Phase 1. "
            "Deletion requests must be explicitly approved via pending.md."
        )


ACTION_REGISTRY: Dict[str, type[BaseAction]] = {
    "log_note": LogNoteAction,
    "create_folder": CreateFolderAction,
    "move_file": MoveFileAction,
    "draft_message": DraftMessageAction,
    "delete": DeleteAction,
    "delete_file": DeleteAction,
    "delete_task": DeleteAction,
    "delete_note": DeleteAction,
}


def get_action(
    name: str,
    params: Optional[Dict[str, Any]] = None,
    task_id: str = "",
    task_title: str = "",
    task_notes: str = "",
    dry_run: bool = False,
) -> BaseAction:
    """Instantiate the corresponding Action class."""
    clean_name = (name or "").lower().strip()
    action_cls = ACTION_REGISTRY.get(clean_name)
    if not action_cls:
        # Check if the name contains 'delete'
        if "delete" in clean_name or "remove" in clean_name:
            action_cls = DeleteAction
        else:
            raise ValueError(f"Unknown or unsupported action: '{name}'. Allowed in Phase 1: log_note, create_folder, move_file, draft_message")
    
    return action_cls(
        params=params or {},
        task_id=task_id,
        task_title=task_title,
        task_notes=task_notes,
        dry_run=dry_run,
    )
