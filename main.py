#!/usr/bin/env python3
"""Command-line entry point for Daybook: Daily task reminder and task-runner.

Commands:
  python main.py digest [--dry-run]  : show today's digest now
  python main.py add                 : add a task interactively
  python main.py done <id>           : mark a task complete
  python main.py pending             : list items awaiting approval
  python main.py approve <id> [--dry-run] : approve a pending action
  python main.py deny <id>           : deny a pending action
  python main.py run [--dry-run]     : start the scheduler and run daily
"""

from __future__ import annotations

import argparse
from datetime import datetime
import sys
from typing import Any, Dict

from config import ensure_daybook_dirs
from tasks import (
    load_tasks,
    add_task,
    mark_task_done,
    TaskValidationError,
)
from approvals import (
    load_pending_items,
    approve_request,
    deny_request,
)
from scheduler import run_daily_digest, start_scheduler_loop
from log import log_entry


def cmd_digest(args: argparse.Namespace) -> int:
    """Run and display today's daily digest."""
    try:
        run_daily_digest(dry_run=args.dry_run, notify=True)
        return 0
    except TaskValidationError as e:
        print(f"\n❌ Configuration Error in tasks.yaml:\n  {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"\n❌ Error during daily digest:\n  {e}", file=sys.stderr)
        return 1


def cmd_pending(args: argparse.Namespace) -> int:
    """List items currently awaiting user approval."""
    items = load_pending_items()
    active = [i for i in items if i.status == "PENDING"]

    print("\n" + "=" * 60)
    print("⏳ DAYBOOK ITEMS AWAITING APPROVAL")
    print("=" * 60)

    if not active:
        print("\n  ✓ No items are waiting for approval.\n")
        return 0

    print(f"\nFound {len(active)} item(s) awaiting your decision:\n")
    for item in active:
        print(f"  • ID: {item.id}")
        print(f"      Task ID:      {item.task_id}")
        print(f"      Title:        {item.title}")
        print(f"      Action:       {item.action}")
        if item.params:
            print(f"      Parameters:   {item.params}")
        print(f"      Reason:       {item.reason}")
        print(f"      Requested At: {item.requested_at}")
        print(f"      Commands:     python main.py approve {item.id}")
        print(f"                    python main.py deny {item.id}\n")

    print("=" * 60 + "\n")
    return 0


def cmd_approve(args: argparse.Namespace) -> int:
    """Approve a pending request."""
    item_id = args.id.strip()
    if not item_id:
        print("❌ Error: Missing required <id> argument.", file=sys.stderr)
        return 1

    success, message = approve_request(item_id, dry_run=args.dry_run)
    if success:
        prefix = "" if message.startswith("[DRY RUN]") else ("[DRY RUN] " if args.dry_run else "✓ ")
        print(f"\n{prefix}{message}\n")
        return 0
    else:
        print(f"\n❌ {message}\n", file=sys.stderr)
        return 1


def cmd_deny(args: argparse.Namespace) -> int:
    """Deny a pending request."""
    item_id = args.id.strip()
    if not item_id:
        print("❌ Error: Missing required <id> argument.", file=sys.stderr)
        return 1

    success, message = deny_request(item_id)
    if success:
        print(f"\n✓ {message}\n")
        return 0
    else:
        print(f"\n❌ {message}\n", file=sys.stderr)
        return 1


def cmd_done(args: argparse.Namespace) -> int:
    """Mark a task complete."""
    task_id = args.id.strip()
    if not task_id:
        print("❌ Error: Missing required <id> argument.", file=sys.stderr)
        return 1

    success, message = mark_task_done(task_id)
    if success:
        log_entry(
            task_id=task_id,
            action="done",
            result="COMPLETED",
            approved_by="user",
        )
        print(f"\n✓ {message}\n")
        return 0
    else:
        print(f"\n❌ {message}\n", file=sys.stderr)
        return 1


def cmd_add(args: argparse.Namespace) -> int:
    """Interactively add a new task."""
    print("\n📝 Add a New Task to Daybook")
    print("-" * 35)

    try:
        task_id = input("Task ID (e.g. morning-check): ").strip()
        if not task_id:
            print("❌ Error: ID cannot be empty.")
            return 1

        title = input("Title: ").strip()
        if not title:
            print("❌ Error: Title cannot be empty.")
            return 1

        notes = input("Notes (optional): ").strip()

        print("\nSchedule type:")
        print("  1. daily (runs every day)")
        print("  2. weekly (runs on specific days)")
        print("  3. once (runs once on specific date)")
        sched_choice = input("Select schedule [1/2/3] (default 1): ").strip() or "1"

        schedule: Dict[str, Any] = {}
        if sched_choice == "2":
            days_input = input("Enter weekdays separated by comma (e.g. mon, wed, fri): ").strip()
            days = [d.strip().lower() for d in days_input.split(",") if d.strip()]
            schedule = {"type": "weekly", "days": days}
        elif sched_choice == "3":
            date_input = input("Enter date (YYYY-MM-DD): ").strip()
            schedule = {"type": "once", "date": date_input}
        else:
            schedule = {"type": "daily"}

        due_time = input("Due time in HH:MM (default 08:00): ").strip() or "08:00"

        mode_choice = input("Mode [remind/delegate] (default remind): ").strip().lower() or "remind"
        if mode_choice not in ("remind", "delegate"):
            print("❌ Error: Invalid mode. Must be 'remind' or 'delegate'.")
            return 1

        action_dict: Any = None
        requires_approval = False

        if mode_choice == "delegate":
            print("\nAllowed actions in Phase 1:")
            print("  1. log_note       (append line to ~/Daybook/journal.md)")
            print("  2. create_folder  (create folder under ~/Daybook/)")
            print("  3. move_file      (move file from ~/Downloads to ~/Daybook/Archive/)")
            print("  4. draft_message  (create draft file under ~/Daybook/drafts/)")
            act_choice = input("Choose action [1/2/3/4]: ").strip()

            action_mapping = {
                "1": "log_note",
                "2": "create_folder",
                "3": "move_file",
                "4": "draft_message",
            }
            action_name = action_mapping.get(act_choice, act_choice)

            params: Dict[str, Any] = {}
            if action_name == "log_note":
                note_text = input("Note text to log (leave blank to use task notes/title): ").strip()
                if note_text:
                    params["text"] = note_text
            elif action_name == "create_folder":
                folder_name = input("Folder name to create under ~/Daybook/: ").strip()
                params["folder"] = folder_name
            elif action_name == "move_file":
                filename = input("Filename in ~/Downloads to move: ").strip()
                params["filename"] = filename
            elif action_name == "draft_message":
                subj = input("Draft subject: ").strip()
                body = input("Draft body text: ").strip()
                params["subject"] = subj
                params["body"] = body

            action_dict = {"name": action_name, **params}

            # Approval question
            appr_input = input("Requires user approval before running? [Y/n] (default Y): ").strip().lower()
            requires_approval = False if appr_input == "n" else True

        new_task = {
            "id": task_id,
            "title": title,
            "notes": notes,
            "schedule": schedule,
            "due_time": due_time,
            "mode": mode_choice,
            "action": action_dict,
            "status": "open",
            "requires_approval": requires_approval,
        }

        success, msg = add_task(new_task)
        if success:
            print(f"\n✓ {msg}\n")
            return 0
        else:
            print(f"\n❌ {msg}\n", file=sys.stderr)
            return 1

    except KeyboardInterrupt:
        print("\nCancelled.")
        return 1


def cmd_run(args: argparse.Namespace) -> int:
    """Start the daily scheduler."""
    start_scheduler_loop(dry_run=args.dry_run)
    return 0


def cmd_autologin(args: argparse.Namespace) -> int:
    """Run automated browser login to EduTrainer."""
    from portal_automation import login_edutainer
    print("\n🌐 Launching automated login to EduTrainer Internship portal...")
    success, msg = login_edutainer(headless=not getattr(args, "headful", False))
    if success:
        mark_task_done("edutraner-intern-login")
        print(f"\n✓ {msg}\n")
        return 0
    else:
        print(f"\n❌ {msg}\n", file=sys.stderr)
        return 1


def cmd_vtudiary(args: argparse.Namespace) -> int:
    """Run automated VTU diary entry."""
    from vtu_automation import enter_vtu_diary
    print("\n🌐 Launching automated VTU Internship Diary entry...")
    success, msg = enter_vtu_diary(
        headless=not getattr(args, "headful", False),
        dry_run=getattr(args, "dry_run", False),
    )
    if success:
        if not getattr(args, "dry_run", False):
            mark_task_done("vtu-portal-diary-entry")
        print(f"\n✓ {msg}\n")
        return 0
    else:
        print(f"\n❌ {msg}\n", file=sys.stderr)
        return 1


def main() -> int:
    ensure_daybook_dirs()

    # Common options parent parser so --dry-run works both before and after subcommand
    base_parser = argparse.ArgumentParser(add_help=False)
    base_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate actions without writing files or changing data",
    )

    parser = argparse.ArgumentParser(
        prog="daybook",
        description="Daybook: macOS daily task reminder and delegable task-runner.",
        parents=[base_parser],
    )

    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # digest
    subparsers.add_parser("digest", parents=[base_parser], help="Show today's digest now")

    # add
    subparsers.add_parser("add", parents=[base_parser], help="Add a task interactively")

    # done <id>
    done_parser = subparsers.add_parser("done", parents=[base_parser], help="Mark a task complete")
    done_parser.add_argument("id", help="Task ID to mark complete")

    # pending
    subparsers.add_parser("pending", parents=[base_parser], help="List items awaiting approval")

    # approve <id>
    appr_parser = subparsers.add_parser("approve", parents=[base_parser], help="Approve a pending action")
    appr_parser.add_argument("id", help="Approval ID or Task ID to approve")

    # deny <id>
    deny_parser = subparsers.add_parser("deny", parents=[base_parser], help="Deny a pending action")
    deny_parser.add_argument("id", help="Approval ID or Task ID to deny")

    # run
    subparsers.add_parser("run", parents=[base_parser], help="Start the scheduler and run daily")

    # autologin
    auto_parser = subparsers.add_parser("autologin", parents=[base_parser], help="Automatically log in to EduTrainer portal")
    auto_parser.add_argument("--headful", action="store_true", help="Launch visible browser window")

    # vtudiary
    vtu_parser = subparsers.add_parser("vtudiary", parents=[base_parser], help="Automatically submit VTU portal diary entry")
    vtu_parser.add_argument("--headful", action="store_true", help="Launch visible browser window")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    commands = {
        "digest": cmd_digest,
        "add": cmd_add,
        "done": cmd_done,
        "pending": cmd_pending,
        "approve": cmd_approve,
        "deny": cmd_deny,
        "run": cmd_run,
        "autologin": cmd_autologin,
        "vtudiary": cmd_vtudiary,
    }

    handler = commands.get(args.command)
    if handler:
        return handler(args)

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
