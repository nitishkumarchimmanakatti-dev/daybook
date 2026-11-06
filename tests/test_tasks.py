"""Tests for tasks module.

Covers:
- Validation of tasks.yaml
- Rejection of malformed entries
- Schedule logic (daily, once, weekly)
- Overdue logic
- Status marking and persistence
"""

from datetime import date, time
from pathlib import Path
import pytest
import yaml

from tasks import (
    load_tasks,
    save_tasks,
    mark_task_done,
    add_task,
    is_task_due_today,
    is_task_overdue,
    TaskValidationError,
    Task,
)


def test_load_valid_tasks(isolated_daybook):
    """Test loading valid tasks from tasks.yaml."""
    tasks_file = isolated_daybook["tasks_file"]
    data = [
        {
            "id": "t1",
            "title": "Task 1",
            "schedule": {"type": "daily"},
            "due_time": "08:00",
            "mode": "remind",
            "status": "open",
        },
        {
            "id": "t2",
            "title": "Task 2",
            "schedule": {"type": "once", "date": "2026-11-04"},
            "due_time": "14:30",
            "mode": "delegate",
            "action": "log_note",
            "status": "open",
            "requires_approval": False,
        },
    ]
    tasks_file.write_text(yaml.safe_dump(data), encoding="utf-8")

    tasks = load_tasks(tasks_file)
    assert len(tasks) == 2
    assert tasks[0].id == "t1"
    assert tasks[0].mode == "remind"
    assert tasks[1].id == "t2"
    assert tasks[1].action_name == "log_note"
    assert tasks[1].requires_approval is False


def test_reject_missing_fields(isolated_daybook):
    """Test rejection when required fields are missing."""
    tasks_file = isolated_daybook["tasks_file"]

    # Missing title
    tasks_file.write_text(yaml.safe_dump([{"id": "t1", "mode": "remind"}]), encoding="utf-8")
    with pytest.raises(TaskValidationError, match="empty or missing 'title'"):
        load_tasks(tasks_file)

    # Missing id
    tasks_file.write_text(yaml.safe_dump([{"title": "No ID", "mode": "remind"}]), encoding="utf-8")
    with pytest.raises(TaskValidationError, match="missing required 'id'"):
        load_tasks(tasks_file)


def test_reject_duplicate_ids(isolated_daybook):
    """Test duplicate IDs are strictly rejected."""
    tasks_file = isolated_daybook["tasks_file"]
    data = [
        {"id": "dup", "title": "First", "mode": "remind", "schedule": {"type": "daily"}},
        {"id": "dup", "title": "Second", "mode": "remind", "schedule": {"type": "daily"}},
    ]
    tasks_file.write_text(yaml.safe_dump(data), encoding="utf-8")
    with pytest.raises(TaskValidationError, match="Duplicate task id 'dup'"):
        load_tasks(tasks_file)


def test_reject_invalid_schedules(isolated_daybook):
    """Test invalid schedule configurations are rejected."""
    tasks_file = isolated_daybook["tasks_file"]

    # Unknown schedule type
    data = [{"id": "bad-sched", "title": "Bad", "mode": "remind", "schedule": {"type": "monthly"}}]
    tasks_file.write_text(yaml.safe_dump(data), encoding="utf-8")
    with pytest.raises(TaskValidationError, match="schedule type 'monthly' is invalid"):
        load_tasks(tasks_file)

    # Once without date
    data = [{"id": "bad-once", "title": "Bad", "mode": "remind", "schedule": {"type": "once"}}]
    tasks_file.write_text(yaml.safe_dump(data), encoding="utf-8")
    with pytest.raises(TaskValidationError, match="requires a valid 'date'"):
        load_tasks(tasks_file)

    # Weekly without valid days
    data = [{"id": "bad-weekly", "title": "Bad", "mode": "remind", "schedule": {"type": "weekly", "days": ["someday"]}}]
    tasks_file.write_text(yaml.safe_dump(data), encoding="utf-8")
    with pytest.raises(TaskValidationError, match="invalid weekday 'someday'"):
        load_tasks(tasks_file)


def test_due_today_and_overdue_logic():
    """Test scheduling calculations for once, daily, and weekly."""
    # Wednesday Nov 4, 2026
    test_wednesday = date(2026, 11, 4)

    # Daily task
    daily_task = Task(
        id="d1", title="Daily", schedule={"type": "daily"},
        due_time="09:00", mode="remind", status="open"
    )
    assert is_task_due_today(daily_task, today=test_wednesday) is True
    # Overdue check: at 10:00 (past 09:00), it's overdue
    assert is_task_overdue(daily_task, today=test_wednesday, current_time=time(10, 0)) is True
    # At 08:30 (before 09:00), not overdue
    assert is_task_overdue(daily_task, today=test_wednesday, current_time=time(8, 30)) is False

    # Once task matching date
    once_today = Task(
        id="o1", title="Once Today", schedule={"type": "once", "date": "2026-11-04"},
        due_time="14:00", mode="remind", status="open"
    )
    assert is_task_due_today(once_today, today=test_wednesday) is True
    assert is_task_overdue(once_today, today=test_wednesday, current_time=time(15, 0)) is True

    # Once task from yesterday: overdue
    once_yesterday = Task(
        id="o2", title="Once Yesterday", schedule={"type": "once", "date": "2026-11-03"},
        due_time="14:00", mode="remind", status="open"
    )
    assert is_task_due_today(once_yesterday, today=test_wednesday) is False
    assert is_task_overdue(once_yesterday, today=test_wednesday, current_time=time(8, 0)) is True

    # Weekly task for Wednesdays
    weekly_wed = Task(
        id="w1", title="Weekly Wed", schedule={"type": "weekly", "days": ["wed", "fri"]},
        due_time="11:00", mode="remind", status="open"
    )
    assert is_task_due_today(weekly_wed, today=test_wednesday) is True

    # Weekly task for Thursdays only
    weekly_thu = Task(
        id="w2", title="Weekly Thu", schedule={"type": "weekly", "days": ["thu"]},
        due_time="11:00", mode="remind", status="open"
    )
    assert is_task_due_today(weekly_thu, today=test_wednesday) is False


def test_mark_task_done(isolated_daybook):
    """Test marking task as complete."""
    tasks_file = isolated_daybook["tasks_file"]
    data = [
        {"id": "finish-me", "title": "Finish", "schedule": {"type": "daily"}, "mode": "remind", "status": "open"}
    ]
    tasks_file.write_text(yaml.safe_dump(data), encoding="utf-8")

    success, msg = mark_task_done("finish-me", tasks_path=tasks_file)
    assert success is True
    assert "Marked task 'finish-me' complete" in msg

    tasks = load_tasks(tasks_file)
    assert tasks[0].status == "done"
    assert is_task_due_today(tasks[0]) is False
