"""Approvals module for Daybook.

Manages ~/Daybook/pending.md and handles approve/deny workflows.
Enforces the strict rule that:
- Deletions NEVER execute automatically and must create a pending approval.
- Actions requiring approval are added to pending.md and wait for user sign-off.
- Denied or unanswered requests are never retried without a new approval.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime
import json
from pathlib import Path
import re
from typing import Any, Dict, List, Optional, Tuple

from config import get_pending_file, ensure_daybook_dirs
from log import log_entry


@dataclass
class PendingApproval:
    id: str
    task_id: str
    title: str
    action: str
    params: Dict[str, Any]
    reason: str
    requested_at: str
    status: str = "PENDING"  # PENDING, APPROVED, DENIED, EXECUTED
    decision_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


ENTRY_DATA_REGEX = re.compile(r"<!-- daybook-data:\s*(\{.*?\})\s*-->")


def load_pending_items(pending_file: Optional[Path] = None) -> List[PendingApproval]:
    """Parse all pending approval entries from pending.md."""
    target_path = pending_file or get_pending_file()
    if not target_path.exists():
        return []

    content = target_path.read_text(encoding="utf-8")
    items: List[PendingApproval] = []
    
    for match in ENTRY_DATA_REGEX.finditer(content):
        try:
            data = json.loads(match.group(1))
            items.append(PendingApproval(
                id=str(data.get("id")),
                task_id=str(data.get("task_id")),
                title=str(data.get("title", "")),
                action=str(data.get("action", "")),
                params=data.get("params", {}),
                reason=str(data.get("reason", "")),
                requested_at=str(data.get("requested_at", "")),
                status=str(data.get("status", "PENDING")),
                decision_at=data.get("decision_at"),
            ))
        except (json.JSONDecodeError, KeyError):
            continue

    return items


def save_pending_items(items: List[PendingApproval], pending_file: Optional[Path] = None) -> None:
    """Write approval entries back to pending.md in a clean, human-readable format."""
    target_path = pending_file or get_pending_file()
    target_path.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "# Daybook Pending Approvals",
        "",
        "This file lists actions that require your explicit approval before execution.",
        "To approve: `python main.py approve <id>`",
        "To deny:    `python main.py deny <id>`",
        "",
    ]

    if not items:
        lines.append("_No approval requests recorded._\n")
    else:
        for item in items:
            badge = f"[{item.status}]"
            lines.append(f"### Request: {item.id} {badge}")
            raw_json = json.dumps(item.to_dict())
            lines.append(f"<!-- daybook-data: {raw_json} -->")
            lines.append(f"- **ID**: `{item.id}`")
            lines.append(f"- **Task ID**: `{item.task_id}`")
            lines.append(f"- **Title**: {item.title}")
            lines.append(f"- **Action**: `{item.action}`")
            if item.params:
                lines.append(f"- **Parameters**: `{json.dumps(item.params)}`")
            lines.append(f"- **Reason**: {item.reason}")
            lines.append(f"- **Requested At**: {item.requested_at}")
            lines.append(f"- **Status**: **{item.status}**")
            if item.decision_at:
                lines.append(f"- **Decision At**: {item.decision_at}")
            lines.append("")

    target_path.write_text("\n".join(lines), encoding="utf-8")


def get_approval_status(task_id: str, pending_file: Optional[Path] = None) -> Optional[PendingApproval]:
    """Find the latest approval item for a given task_id."""
    items = load_pending_items(pending_file)
    for item in reversed(items):
        if item.task_id == task_id or item.id == task_id:
            return item
    return None


def add_pending_request(
    task_id: str,
    title: str,
    action: str,
    params: Dict[str, Any],
    reason: str,
    pending_file: Optional[Path] = None,
) -> PendingApproval:
    """Add a new approval request to pending.md if not already pending."""
    items = load_pending_items(pending_file)
    
    # Check if this task already has an active PENDING request
    for item in items:
        if (item.task_id == task_id or item.id == task_id) and item.status == "PENDING":
            return item

    # Use task_id as approval id, or disambiguate if task_id was used previously
    existing_ids = {i.id for i in items}
    req_id = task_id
    if req_id in existing_ids:
        counter = 1
        while f"{task_id}-{counter}" in existing_ids:
            counter += 1
        req_id = f"{task_id}-{counter}"

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    item = PendingApproval(
        id=req_id,
        task_id=task_id,
        title=title,
        action=action,
        params=params,
        reason=reason,
        requested_at=now_str,
        status="PENDING",
    )

    items.append(item)
    save_pending_items(items, pending_file)

    # Log that approval is pending
    log_entry(
        task_id=task_id,
        action=action,
        result=f"PENDING_APPROVAL (id: {req_id})",
        approved_by="",
    )

    return item


def approve_request(
    item_id: str,
    dry_run: bool = False,
    pending_file: Optional[Path] = None,
) -> Tuple[bool, str]:
    """Approve a pending request and execute the associated action."""
    # Import here to avoid circular dependencies
    from actions import get_action

    items = load_pending_items(pending_file)
    target_item: Optional[PendingApproval] = None

    for item in items:
        if item.id == item_id or item.task_id == item_id:
            target_item = item
            break

    if not target_item:
        return False, f"No approval request found for ID '{item_id}'."

    if target_item.status != "PENDING":
        return False, f"Request '{item_id}' is already {target_item.status}."

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # If action is deletion:
    # Phase 1 safety: Deletions are never performed automatically.
    # An approved deletion records explicit user permission.
    if target_item.action.startswith("delete"):
        target_item.status = "APPROVED"
        target_item.decision_at = now_str
        save_pending_items(items, pending_file)
        
        log_entry(
            task_id=target_item.task_id,
            action=target_item.action,
            result="APPROVED_BY_USER",
            approved_by="user",
        )
        return True, f"Approved deletion request '{item_id}'. Recorded explicit user permission."

    # For other actions, execute safely
    action_instance = get_action(
        name=target_item.action,
        params=target_item.params,
        task_id=target_item.task_id,
        task_title=target_item.title,
        dry_run=dry_run,
    )

    try:
        result = action_instance.execute()
        if not dry_run:
            target_item.status = "EXECUTED"
            target_item.decision_at = now_str
            save_pending_items(items, pending_file)
            log_entry(
                task_id=target_item.task_id,
                action=target_item.action,
                result=result,
                approved_by="user",
            )
        return True, result
    except Exception as e:
        error_msg = f"Failed to execute approved action: {e}"
        if not dry_run:
            log_entry(
                task_id=target_item.task_id,
                action=target_item.action,
                result=f"ERROR: {e}",
                approved_by="user",
            )
        return False, error_msg


def deny_request(
    item_id: str,
    pending_file: Optional[Path] = None,
) -> Tuple[bool, str]:
    """Deny a pending request and mark it as DENIED so it is never retried."""
    items = load_pending_items(pending_file)
    target_item: Optional[PendingApproval] = None

    for item in items:
        if item.id == item_id or item.task_id == item_id:
            target_item = item
            break

    if not target_item:
        return False, f"No approval request found for ID '{item_id}'."

    if target_item.status != "PENDING":
        return False, f"Request '{item_id}' is already {target_item.status}."

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    target_item.status = "DENIED"
    target_item.decision_at = now_str
    save_pending_items(items, pending_file)

    log_entry(
        task_id=target_item.task_id,
        action=target_item.action,
        result="DENIED",
        approved_by="user",
    )

    return True, f"Denied request '{item_id}'. It will not be retried without a new approval."
