import time
from datetime import date 

Today = date.today()
 

class ToDoTask:
    def __init__ (self, date_of_task, time_of_task, description, duration, importance, note):

        self.date = date_of_task.isoformat()
        self.time = time_of_task
        self.description = description
        self.duration = duration
        self.importance = importance
        self.note = note



### Test Block ###

if __name__ == "__main__":
    task = ToDoTask(
        date.today(),
        "0900",
        "test the class",
        60,
        "High",
        "test"
    )
    print(task.date, task.time, task.description, task.duration, task.importance, task.note)