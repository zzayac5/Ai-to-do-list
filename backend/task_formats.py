from datetime import date, datetime, time, timedelta
from typing import List, Optional
import math

class ToDoTask:
    def __init__(
        self,
        date_of_task: date,
        time_of_task: time,
        description: str,

        optimistic_minutes: int,
        most_likely_minutes: int,
        pessimistic_minutes: int,

        importance: str,
        note: str,

        due_date_flexible: bool = True,
        required_resources: Optional[List[str]] = None,
        required_people: Optional[List[str]] = None,
        dependencies: Optional[List["ToDoTask"]] = None,
        recurring: bool = False
    ):
        # --- Temporal base ---
        self.start_datetime = datetime.combine(date_of_task, time_of_task)

        self.optimistic_minutes = optimistic_minutes
        self.most_likely_minutes = most_likely_minutes
        self.pessimistic_minutes = pessimistic_minutes

        # --- PERT calculations ---
        self.expected_duration_minutes = self._expected_duration()
        self.std_dev_minutes = self._standard_deviation()

        self.end_datetime = self.start_datetime + timedelta(
            minutes=self.expected_duration_minutes
        )

        # --- Structural constraints ---
        self.dependencies = dependencies or []
        self.required_resources = required_resources or []
        self.required_people = required_people or []
        self.recurring = recurring

        # --- Flexibility & metadata ---
        self.due_date_flexible = due_date_flexible
        self.importance = importance
        self.note = note
        self.description = description

    # ---------- Statistical methods ----------

    def _expected_duration(self) -> float:
        return (
            self.optimistic_minutes
            + 4 * self.most_likely_minutes
            + self.pessimistic_minutes
        ) / 6

    def _standard_deviation(self) -> float:
        return (self.pessimistic_minutes - self.optimistic_minutes) / 6

    # ---------- Convenience methods ----------

    def start_str(self) -> str:
        return self.start_datetime.ctime()

    def end_str(self) -> str:
        return self.end_datetime.ctime()

    def slack_risk_score(self) -> float:
        """
        Simple heuristic:
        higher SD + inflexible due date = higher risk
        """
        base_risk = self.std_dev_minutes
        return base_risk * (2 if not self.due_date_flexible else 1)



if __name__ == "__main__":
    task = ToDoTask(
        date.today(),
        time(9, 0),
        "Write proposal draft",

        optimistic_minutes=60,
        most_likely_minutes=90,
        pessimistic_minutes=150,

        importance="High",
        note="Needs review by legal",

        due_date_flexible=False,
        required_people=["Alex"],
        required_resources=["Docs"],
        recurring=False
    )

    print("Start:", task.start_str())
    print("Expected End:", task.end_str())
    print("Expected Duration:", task.expected_duration_minutes, "minutes")
    print("Std Dev:", round(task.std_dev_minutes, 2), "minutes")
    print("Risk Score:", task.slack_risk_score())
