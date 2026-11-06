"""Tasks module for Daybook.

Handles loading, validating, querying, and updating tasks.yaml.
Strictly refuses to run with malformed entries.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, time
import os
from pathlib import Path
import re
import tempfile
from typing import Any, Dict, List, Optional, Tuple, Union
import yaml

from config import get_tasks_file


class TaskValidationError(Exception):
    """Raised when tasks.yaml contains invalid or malformed entries."""
    pass


VALID_MODES = {"remind", "delegate"}
VALID_STATUSES = {"open", "done", "skipped"}
VALID_SCHEDULE_TYPES = {"once", "daily", "weekly"}
VALID_DAYS = {"mon", "tue", "wed", "thu", "fri", "sat", "sun"}
TIME_REGEX = re.compile(r"^([01]\d|2[0-3]):([0-5]\d)$")


@dataclass
class Task:
    id: str
    title: str
    notes: str = ""
    schedule: Dict[str, Any] = field(default_factory=dict)
    due_time: str = "08:00"
    mode: str = "remind"
    action: Optional[Union[str, Dict[str, Any]]] = None
    status: str = "open"
    requires_approval: bool = True
    raw_data: Dict[str, Any] = field(default_factory=dict)

    @property
    def action_name(self) -> Optional[str]:
        if not self.action:
            return None
        if isinstance(self.action, str):
            return self.action.strip()
        if isinstance(self.action, dict):
            return str(self.action.get("name") or self.action.get("type", "")).strip()
        return None

    @property
    def action_params(self) -> Dict[str, Any]:
        if isinstance(self.action, dict):
            # Return dict without the 'name' key, or the explicit 'params' dict
            if "params" in self.action and isinstance(self.action["params"], dict):
                return self.action["params"]
            return {k: v for k, v in self.action.items() if k not in ("name", "type")}
        return {}


def parse_date(value: Any) -> Optional[date]:
    """Parse a date from string or date object."""
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            return datetime.strptime(value.strip(), "%Y-%m-%d").date()
        except ValueError:
            return None
    return None


def parse_time(value: Any) -> Optional[time]:
    """Parse HH:MM string into time object."""
    if isinstance(value, time):
        return value
    if isinstance(value, str):
        m = TIME_REGEX.match(value.strip())
        if m:
            return time(hour=int(m.group(1)), minute=int(m.group(2)))
    return None


def validate_task_dict(raw: Dict[str, Any], index: int, seen_ids: set[str]) -> Task:
    """Strictly validate a raw task dictionary from tasks.yaml."""
    if not isinstance(raw, dict):
        raise TaskValidationError(f"Task at index {index} must be a dictionary/mapping.")

    # 1. ID validation
    task_id = str(raw.get("id", "")).strip()
    if not task_id:
        raise TaskValidationError(f"Task at index {index} is missing required 'id'.")
    if task_id in seen_ids:
        raise TaskValidationError(f"Duplicate task id '{task_id}' found at index {index}.")
    seen_ids.add(task_id)

    # 2. Title validation
    title = str(raw.get("title", "")).strip()
    if not title:
        raise TaskValidationError(f"Task '{task_id}' has an empty or missing 'title'.")

    # 3. Mode validation
    mode = str(raw.get("mode", "")).strip().lower()
    if mode not in VALID_MODES:
        raise TaskValidationError(
            f"Task '{task_id}' has invalid mode '{mode}'. Allowed: {sorted(VALID_MODES)}"
        )

    # 4. Status validation
    status = str(raw.get("status", "open")).strip().lower()
    if status not in VALID_STATUSES:
        raise TaskValidationError(
            f"Task '{task_id}' has invalid status '{status}'. Allowed: {sorted(VALID_STATUSES)}"
        )

    # 5. Due time validation
    due_time_raw = str(raw.get("due_time", "08:00")).strip()
    if not TIME_REGEX.match(due_time_raw):
        raise TaskValidationError(
            f"Task '{task_id}' has invalid due_time '{due_time_raw}'. Expected HH:MM in 24-hr format."
        )

    # 6. Schedule validation
    schedule = raw.get("schedule")
    if not isinstance(schedule, dict):
        raise TaskValidationError(f"Task '{task_id}' must have a 'schedule' dictionary.")
    
    sched_type = str(schedule.get("type", "")).strip().lower()
    if sched_type not in VALID_SCHEDULE_TYPES:
        raise TaskValidationError(
            f"Task '{task_id}' schedule type '{sched_type}' is invalid. Allowed: {sorted(VALID_SCHEDULE_TYPES)}"
        )

    if sched_type == "once":
        d_val = schedule.get("date")
        if not d_val or not parse_date(d_val):
            raise TaskValidationError(
                f"Task '{task_id}' with schedule 'once' requires a valid 'date' in YYYY-MM-DD format."
            )
    elif sched_type == "weekly":
        days = schedule.get("days")
        if not isinstance(days, list) or len(days) == 0:
            raise TaskValidationError(
                f"Task '{task_id}' with schedule 'weekly' requires a non-empty list of 'days'."
            )
        for d in days:
            d_clean = str(d).strip().lower()[:3]
            if d_clean not in VALID_DAYS:
                raise TaskValidationError(
                    f"Task '{task_id}' has invalid weekday '{d}'. Allowed: {sorted(VALID_DAYS)}"
                )

    # 7. Action and Approval defaults
    action = raw.get("action")
    if mode == "delegate" and not action:
        raise TaskValidationError(
            f"Task '{task_id}' has mode 'delegate' but specifies no 'action'."
        )

    # Default requires_approval to True for any task with an action
    if "requires_approval" in raw:
        requires_approval = bool(raw["requires_approval"])
    else:
        requires_approval = True if action else False

    notes = str(raw.get("notes", "")).strip()

    return Task(
        id=task_id,
        title=title,
        notes=notes,
        schedule=schedule,
        due_time=due_time_raw,
        mode=mode,
        action=action,
        status=status,
        requires_approval=requires_approval,
        raw_data=raw,
    )


def load_tasks(tasks_path: Optional[Path] = None) -> List[Task]:
    """Load and validate all tasks from tasks.yaml. Refuses to run if malformed."""
    target_path = tasks_path or get_tasks_file()
    if not target_path.exists():
        return []

    try:
        content = target_path.read_text(encoding="utf-8")
        data = yaml.safe_load(content)
    except yaml.YAMLError as e:
        raise TaskValidationError(f"YAML syntax error in {target_path}: {e}")

    if data is None:
        return []
    if not isinstance(data, list):
        raise TaskValidationError(f"Expected top-level list of tasks in {target_path}.")

    tasks: List[Task] = []
    seen_ids: set[str] = set()
    for idx, raw in enumerate(data):
        task = validate_task_dict(raw, idx, seen_ids)
        tasks.append(task)

    return tasks


def is_task_due_on(task: Task, target_date: date) -> bool:
    """Determine if a task is scheduled for target_date."""
    sched_type = str(task.schedule.get("type", "")).strip().lower()
    if sched_type == "daily":
        return True
    elif sched_type == "once":
        task_date = parse_date(task.schedule.get("date"))
        return task_date == target_date
    elif sched_type == "weekly":
        day_str = target_date.strftime("%a").lower()
        task_days = [str(d).strip().lower()[:3] for d in task.schedule.get("days", [])]
        return day_str in task_days
    return False


def is_task_due_today(task: Task, today: Optional[date] = None) -> bool:
    """Check if task is scheduled for today and is open."""
    current_date = today or date.today()
    if task.status != "open":
        return False
    return is_task_due_on(task, current_date)


def is_task_overdue(task: Task, today: Optional[date] = None, current_time: Optional[time] = None) -> bool:
    """Check if an open task is overdue relative to target date and time."""
    if task.status != "open":
        return False

    ref_date = today or date.today()
    ref_time = current_time or datetime.now().time()
    sched_type = str(task.schedule.get("type", "")).strip().lower()

    if sched_type == "once":
        task_date = parse_date(task.schedule.get("date"))
        if not task_date:
            return False
        if task_date < ref_date:
            return True
        if task_date == ref_date:
            task_time = parse_time(task.due_time)
            if task_time and task_time < ref_time:
                return True
        return False

    elif sched_type in ("daily", "weekly"):
        # For recurring tasks, if due today and past due_time, it is overdue for today
        if is_task_due_on(task, ref_date):
            task_time = parse_time(task.due_time)
            if task_time and task_time < ref_time:
                return True

    return False


def save_tasks(tasks: List[Task], tasks_path: Optional[Path] = None) -> None:
    """Atomically write tasks back to tasks.yaml."""
    target_path = tasks_path or get_tasks_file()
    target_path.parent.mkdir(parents=True, exist_ok=True)

    data = []
    for t in tasks:
        # Reconstruct clean dict
        entry: Dict[str, Any] = {
            "id": t.id,
            "title": t.title,
            "schedule": t.schedule,
            "due_time": t.due_time,
            "mode": t.mode,
            "status": t.status,
            "requires_approval": t.requires_approval,
        }
        if t.notes:
            entry["notes"] = t.notes
        if t.action:
            entry["action"] = t.action
        data.append(entry)

    # Atomic write via temporary file
    temp_dir = target_path.parent
    with tempfile.NamedTemporaryFile("w", dir=temp_dir, delete=False, encoding="utf-8") as tf:
        yaml.safe_dump(data, tf, sort_keys=False, default_flow_style=False)
        temp_name = tf.name

    os.replace(temp_name, target_path)


def mark_task_done(task_id: str, tasks_path: Optional[Path] = None) -> Tuple[bool, str]:
    """Mark a task complete in tasks.yaml."""
    tasks = load_tasks(tasks_path)
    for t in tasks:
        if t.id == task_id:
            if t.status == "done":
                return True, f"Task '{task_id}' was already marked done."
            t.status = "done"
            save_tasks(tasks, tasks_path)
            return True, f"Marked task '{task_id}' complete."
    return False, f"Task '{task_id}' not found."


def add_task(new_task_dict: Dict[str, Any], tasks_path: Optional[Path] = None) -> Tuple[bool, str]:
    """Validate and add a new task to tasks.yaml."""
    tasks = load_tasks(tasks_path)
    seen_ids = {t.id for t in tasks}
    
    try:
        validated = validate_task_dict(new_task_dict, len(tasks), seen_ids)
    except TaskValidationError as e:
        return False, str(e)

    tasks.append(validated)
    save_tasks(tasks, tasks_path)
    return True, f"Task '{validated.id}' added successfully."
