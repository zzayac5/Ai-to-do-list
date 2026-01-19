from datetime import date, time
from task_formats import ToDoTask


def test_end_time_calculation():
    task = ToDoTask(
        date(2026, 1, 20),
        time(9, 0),
        "Test task",
        optimistic_minutes=30,
        most_likely_minutes=60,
        pessimistic_minutes=90,
        importance="Medium",
        note="Test",
    )

    # Expected duration = (30 + 4*60 + 90) / 6 = 60 minutes
    assert task.end_datetime.hour == 10
    assert task.end_datetime.minute == 0

def test_start_datetime():
    task = ToDoTask(
        date(2026, 2, 1),
        time(14, 30),
        "Start time test",
        10, 20, 30,
        importance="Low",
        note=""
    )

    assert task.start_datetime.year == 2026
    assert task.start_datetime.hour == 14
    assert task.start_datetime.minute == 30


def test_standard_deviation():
    task = ToDoTask(
        date(2026, 1, 1),
        time(8, 0),
        "SD test",
        30, 60, 90,
        "Low",
        ""
    )

    # (90 - 30) / 6 = 10
    assert task.std_dev_minutes == 10


def test_crossing_midnight():
    task = ToDoTask(
        date(2026, 1, 1),
        time(23, 30),
        "Late task",
        30, 60, 90,
        importance="Medium",
        note=""
    )

    assert task.end_datetime.day == 2


def test_slack_risk_score():
    flexible_task = ToDoTask(
        date(2026, 1, 1),
        time(9, 0),
        "Flexible",
        30, 60, 90,
        importance="Low",
        note="",
        due_date_flexible=True
    )

    inflexible_task = ToDoTask(
        date(2026, 1, 1),
        time(9, 0),
        "Inflexible",
        30, 60, 90,
        importance="High",
        note="",
        due_date_flexible=False
    )

    assert inflexible_task.slack_risk_score() > flexible_task.slack_risk_score()

def test_missing_date_raises_error():
    try:
        ToDoTask(
            None,
            time(9, 0),
            "Invalid task",
            30, 60, 90,
            importance="Low",
            note=""
        )
        assert False, "Expected ValueError for missing date"
    except ValueError:
        assert True

if __name__ == "__main__":
    test_start_datetime()
    test_end_time_calculation()
    test_standard_deviation()
    test_crossing_midnight()
    test_slack_risk_score()
    test_missing_date_raises_error()

    print("All tests ran.")
