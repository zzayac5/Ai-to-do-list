from datetime import date 

class ToDoTask:
    def __init__ (self, date, time, description, duration, importance, note):

        self.date = date
        self.time = time
        self.description = description
        self.duration = duration
        self.importance = importance
        self.note = note

    
    def establish_importance (self):
        if self.date is date.today():
            raise ValueError("no time left")
        else:
            pass
        

