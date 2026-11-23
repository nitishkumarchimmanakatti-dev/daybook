"""Scheduler and daily flow engine for Daybook.

Orchestrates the daily digest:
1. Reads tasks.yaml and finds tasks due today and overdue.
2. Identifies items waiting for approval in pending.md.
3. Automatically executes delegable tasks with permitted actions if approval is not required.
4. Adds unapproved or deletion actions to pending.md.
5. Logs all events to daybook_log.csv.
6. Emits desktop notifications and prints terminal summaries.
7. Schedules daily execution at the configured time (default 08:00).
"""

from __future__ import annotations

from datetime import date, datetime, time
import time as time_module
from typing import Any, Dict, List, Optional, Tuple

from config import get_digest_time, ensure_daybook_dirs, get_log_file
from tasks import (
    Task,
    load_tasks,
    is_task_due_today,
    is_task_overdue,
    mark_task_done,
)
from actions import get_action, BaseAction, ActionSecurityError, ActionExecutionError
from approvals import (
    load_pending_items,
    get_approval_status,
    add_pending_request,
    save_pending_items,
    PendingApproval,
)
from log import log_entry
from notify import send_macos_notification, print_digest


def run_daily_digest(
    dry_run: bool = False,
    notify: bool = True,
    today_override: Optional[date] = None,
    now_override: Optional[time] = None,
) -> Dict[str, Any]:
    """Execute the full daily digest flow according to Daybook rules."""
    ensure_daybook_dirs()
    
    current_date = today_override or date.today()
    current_time = now_override or datetime.now().time()
    current_dt = datetime.combine(current_date, current_time)

    # 1. Load all tasks
    tasks = load_tasks()

    # 2. Categorize tasks
    due_tasks: List[Task] = []
    overdue_tasks: List[Task] = []

    for t in tasks:
        if is_task_due_today(t, today=current_date):
            due_tasks.append(t)
        elif is_task_overdue(t, today=current_date, current_time=current_time):
            overdue_tasks.append(t)

    executed_actions: List[Dict[str, str]] = []

    # 3. Process delegate tasks due today
    for t in due_tasks:
        if t.mode != "delegate" or not t.action_name:
            # Remind mode: log reminder
            if not dry_run:
                log_entry(
                    task_id=t.id,
                    action="remind",
                    result="NOTIFIED",
                    approved_by="system",
                    timestamp=current_dt.strftime("%Y-%m-%d %H:%M:%S"),
                )
            continue

        action_name = t.action_name

        # Check existing approval status first (enforces: denied/unanswered never retried)
        existing_approval = get_approval_status(t.id)
        if existing_approval:
            if existing_approval.status == "DENIED":
                executed_actions.append({
                    "task_id": t.id,
                    "action": action_name,
                    "result": "SKIPPED (previously denied by user)",
                })
                continue
            elif existing_approval.status == "PENDING":
                executed_actions.append({
                    "task_id": t.id,
                    "action": action_name,
                    "result": f"Still awaiting approval (id: {existing_approval.id})",
                })
                continue

        # SAFETY RULE 1: Deletions are NEVER automatic under any circumstances
        is_delete = (
            action_name.startswith("delete")
            or "delete" in action_name
            or "remove" in action_name
        )

        if is_delete:
            if existing_approval and existing_approval.status == "APPROVED":
                executed_actions.append({
                    "task_id": t.id,
                    "action": action_name,
                    "result": "Approved deletion confirmed by user",
                })
                continue

            # Create a pending approval entry and do nothing else
            pending_item = add_pending_request(
                task_id=t.id,
                title=t.title,
                action=action_name,
                params=t.action_params,
                reason="Deletion request: deleting any file, note, or task is never done automatically and requires explicit approval.",
            )
            executed_actions.append({
                "task_id": t.id,
                "action": action_name,
                "result": f"Awaiting explicit approval (id: {pending_item.id})",
            })
            continue

        # Instantiate action to test permission rules
        try:
            action_instance = get_action(
                name=action_name,
                params=t.action_params,
                task_id=t.id,
                task_title=t.title,
                task_notes=t.notes,
                dry_run=dry_run,
            )
        except Exception as e:
            if not dry_run:
                log_entry(
                    task_id=t.id,
                    action=action_name,
                    result=f"ERROR: {e}",
                    approved_by="system",
                )
            executed_actions.append({
                "task_id": t.id,
                "action": action_name,
                "result": f"ERROR: {e}",
            })
            continue

        # SAFETY RULE 2:
        # Every action that modifies data requires approval unless:
        # requires_approval: false AND action in (log_note, draft_message)
        can_auto = action_instance.can_auto_execute(t.requires_approval)

        if can_auto:
            try:
                res = action_instance.execute()
                if not dry_run:
                    log_entry(
                        task_id=t.id,
                        action=action_name,
                        result=res,
                        approved_by="system",
                        timestamp=current_dt.strftime("%Y-%m-%d %H:%M:%S"),
                    )
                executed_actions.append({
                    "task_id": t.id,
                    "action": action_name,
                    "result": res,
                })
            except Exception as e:
                err_res = f"Execution failed: {e}"
                if not dry_run:
                    log_entry(
                        task_id=t.id,
                        action=action_name,
                        result=err_res,
                        approved_by="system",
                    )
                executed_actions.append({
                    "task_id": t.id,
                    "action": action_name,
                    "result": err_res,
                })
        else:
            # Action requires user approval
            existing_approval = get_approval_status(t.id)

            if existing_approval:
                if existing_approval.status == "DENIED":
                    # Denied requests are never retried without a new approval
                    executed_actions.append({
                        "task_id": t.id,
                        "action": action_name,
                        "result": "SKIPPED (previously denied by user)",
                    })
                    continue
                elif existing_approval.status == "APPROVED":
                    # User approved: run now
                    try:
                        res = action_instance.execute()
                        if not dry_run:
                            existing_approval.status = "EXECUTED"
                            all_items = load_pending_items()
                            for idx, it in enumerate(all_items):
                                if it.id == existing_approval.id:
                                    all_items[idx] = existing_approval
                            save_pending_items(all_items)
                            log_entry(
                                task_id=t.id,
                                action=action_name,
                                result=res,
                                approved_by="user",
                            )
                        executed_actions.append({
                            "task_id": t.id,
                            "action": action_name,
                            "result": f"Executed approved action: {res}",
                        })
                    except Exception as e:
                        err_res = f"Approved execution failed: {e}"
                        executed_actions.append({
                            "task_id": t.id,
                            "action": action_name,
                            "result": err_res,
                        })
                    continue
                elif existing_approval.status == "PENDING":
                    executed_actions.append({
                        "task_id": t.id,
                        "action": action_name,
                        "result": f"Still awaiting approval (id: {existing_approval.id})",
                    })
                    continue

            # Need to create pending approval
            reason = (
                f"Action '{action_name}' modifies data and requires approval."
                if t.requires_approval
                else f"Action '{action_name}' is not permitted to auto-execute without approval."
            )
            pending_item = add_pending_request(
                task_id=t.id,
                title=t.title,
                action=action_name,
                params=t.action_params,
                reason=reason,
            )
            executed_actions.append({
                "task_id": t.id,
                "action": action_name,
                "result": f"Added to pending approvals (id: {pending_item.id})",
            })

    # 4. Gather pending items awaiting approval
    all_pending = load_pending_items()
    active_pending = [item for item in all_pending if item.status == "PENDING"]

    # 5. Output / Notifications
    if notify:
        print_digest(
            due_tasks=due_tasks,
            overdue_tasks=overdue_tasks,
            pending_items=active_pending,
            executed_actions=executed_actions,
            current_dt=current_dt,
        )

        # macOS Desktop Notification
        mac_msg = f"{len(due_tasks)} task(s) due today"
        if active_pending:
            mac_msg += f", {len(active_pending)} awaiting approval"
        send_macos_notification(
            title="Daybook Daily Digest",
            subtitle=f"{current_date.strftime('%b %d')}",
            message=mac_msg,
        )

    # 6. Check 30-minute fallback automation if running past 11:30 AM
    check_30min_fallbacks()

    return {
        "due_tasks": due_tasks,
        "overdue_tasks": overdue_tasks,
        "pending_items": active_pending,
        "executed_actions": executed_actions,
    }


def check_30min_fallbacks() -> None:
    """If 30 minutes pass after 11:00 AM without reply, perform automatic login & VTU diary entry."""
    now = datetime.now()
    if (now.hour > 11) or (now.hour == 11 and now.minute >= 30):
        today_str = now.strftime("%Y-%m-%d")
        
        # Check if already completed today in log
        completed_today = set()
        log_file = get_log_file()
        if log_file.exists():
            try:
                for line in log_file.read_text(encoding="utf-8").splitlines():
                    if line.startswith(today_str) and "SUCCESS" in line:
                        parts = line.split(",")
                        if len(parts) >= 2:
                            completed_today.add(parts[1].strip())
            except Exception:
                pass

        tasks = load_tasks()
        for t in tasks:
            if t.id == "edutraner-intern-login" and t.status == "open":
                if "edutraner-intern-login" not in completed_today:
                    try:
                        from portal_automation import login_edutainer
                        login_edutainer(headless=True)
                    except Exception as e:
                        print(f"EduTrainer auto-login fallback error: {e}")

            elif t.id == "vtu-portal-diary-entry" and t.status == "open":
                if "vtu-portal-diary-entry" not in completed_today:
                    try:
                        from vtu_automation import enter_vtu_diary
                        enter_vtu_diary(headless=True, dry_run=False)
                    except Exception as e:
                        print(f"VTU diary entry fallback error: {e}")


def start_scheduler_loop(dry_run: bool = False, poll_interval_seconds: int = 20) -> None:
    """Run continuous scheduler, triggering digest daily at configured time."""
    target_time_str = get_digest_time()
    try:
        target_hour, target_minute = map(int, target_time_str.split(":"))
    except ValueError:
        target_hour, target_minute = 8, 0

    print(f"⏰ Daybook scheduler started.")
    print(f"📅 Daily digest scheduled for {target_hour:02d}:{target_minute:02d} every day.")
    if dry_run:
        print("🔍 Running in DRY RUN mode (no changes will be persisted).")
    print("Press Ctrl+C to stop.\n")

    last_run_date: Optional[date] = None

    try:
        while True:
            now = datetime.now()
            today = now.date()

            if (
                now.hour == target_hour
                and now.minute == target_minute
                and last_run_date != today
            ):
                print(f"\n🔔 Triggering scheduled daily digest for {today}...")
                run_daily_digest(dry_run=dry_run, notify=True)
                last_run_date = today

            time_module.sleep(poll_interval_seconds)
    except KeyboardInterrupt:
        print("\n🛑 Daybook scheduler stopped gracefully.")
