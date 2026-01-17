# backend/task_formats.py
from datetime import datetime, timedelta
from typing import List
from math import sqrt

class ToDoTask:
    def __init__(self, task_input):
        self.description = task_input.description

        self.start_datetime = self._build_start_datetime(
            task_input.date_of_task,
            task_input.time_of_task
        )

        self.optimistic = task_input.optimistic_minutes
        self.most_likely = task_input.most_likely_minutes
        self.pessimistic = task_input.pessimistic_minutes

        self.expected_duration = self._expected_duration()
        self.std_dev = self._standard_deviation()

        self.end_datetime = self.start_datetime + timedelta(
            minutes=self.expected_duration
        )

        self.importance = task_input.importance
        self.note = task_input.note
        self.flexible = task_input.due_date_flexible

    def _build_start_datetime(self, d, t):
        if d is None or t is None:
            raise ValueError("Task must have date and time before scheduling.")
        return datetime.combine(d, t)

    def _expected_duration(self):
        return (self.optimistic + 4*self.most_likely + self.pessimistic) / 6

    def _standard_deviation(self):
        return (self.pessimistic - self.optimistic) / 6

    def summary(self):
        return {
            "description": self.description,
            "start": self.start_datetime.isoformat(),
            "end": self.end_datetime.isoformat(),
            "risk": round(self.std_dev, 2)
        }

class SubTask:
    def __init__(self, task_input, sub_task_input):
        super().__init__(task_input)
        self.sub_task_input = sub_task_input
        