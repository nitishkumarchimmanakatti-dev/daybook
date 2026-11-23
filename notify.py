"""Notification module for Daybook.

Provides macOS desktop notifications via osascript and
formatted terminal output for daily digests and status updates.
"""

from __future__ import annotations

from datetime import datetime
import platform
import subprocess
from typing import Any, Dict, List, Optional


def send_macos_notification(
    title: str,
    message: str,
    subtitle: str = "",
    sound: str = "default",
) -> bool:
    """Trigger a native macOS desktop notification using AppleScript.

    Gracefully falls back if osascript is unavailable or fails.
    """
    if platform.system() != "Darwin":
        return False

    def escape_applescript(s: str) -> str:
        return s.replace("\\", "\\\\").replace('"', '\\"')

    safe_title = escape_applescript(title)
    safe_subtitle = escape_applescript(subtitle)
    safe_msg = escape_applescript(message)

    script = f'display notification "{safe_msg}" with title "{safe_title}"'
    if safe_subtitle:
        script += f' subtitle "{safe_subtitle}"'
    if sound:
        script += f' sound name "{sound}"'

    try:
        subprocess.run(
            ["osascript", "-e", script],
            check=True,
            capture_output=True,
            timeout=5,
        )
        return True
    except (subprocess.SubprocessError, FileNotFoundError, OSError):
        # Graceful fallback in non-interactive, headless, or test environments
        return False


def print_digest(
    due_tasks: List[Any],
    overdue_tasks: List[Any],
    pending_items: List[Any],
    executed_actions: Optional[List[Dict[str, str]]] = None,
    current_dt: Optional[datetime] = None,
) -> None:
    """Print a clean, structured summary in the terminal."""
    dt = current_dt or datetime.now()
    date_str = dt.strftime("%A, %B %d, %Y")
    time_str = dt.strftime("%H:%M")

    print("\n" + "=" * 60)
    print(f"📖 DAYBOOK DAILY DIGEST — {date_str} ({time_str})")
    print("=" * 60)

    # 1. Due Today
    print(f"\n📌 TASKS DUE TODAY ({len(due_tasks)}):")
    if not due_tasks:
        print("  ✓ No open tasks due today.")
    else:
        for t in due_tasks:
            mode_tag = "[DELEGATE]" if t.mode == "delegate" else "[REMIND]"
            approval_tag = " (requires approval)" if t.requires_approval and t.action else ""
            print(f"  • {mode_tag} [{t.id}] {t.title} (due {t.due_time}){approval_tag}")
            if t.notes:
                print(f"      Notes: {t.notes}")
            if t.action:
                print(f"      Action: {t.action_name}")

    # 2. Overdue Tasks
    print(f"\n⚠️  OVERDUE TASKS ({len(overdue_tasks)}):")
    if not overdue_tasks:
        print("  ✓ No overdue tasks.")
    else:
        for t in overdue_tasks:
            print(f"  • [{t.id}] {t.title} (was due {t.due_time})")

    # 3. Pending Approvals
    print(f"\n⏳ ITEMS AWAITING APPROVAL ({len(pending_items)}):")
    if not pending_items:
        print("  ✓ No pending approvals.")
    else:
        for item in pending_items:
            print(f"  • ID: {item.id} | Action: {item.action}")
            print(f"      Task: {item.title} (task_id: {item.task_id})")
            print(f"      Reason: {item.reason}")
            print(f"      To approve: python main.py approve {item.id}")
            print(f"      To deny:    python main.py deny {item.id}")

    # 4. Actions Executed
    if executed_actions:
        print(f"\n⚙️  ACTIONS PROCESSED ({len(executed_actions)}):")
        for act in executed_actions:
            print(f"  • [{act.get('task_id', '')}] {act.get('action', '')}: {act.get('result', '')}")

    print("\n" + "=" * 60 + "\n")
