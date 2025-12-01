import sqlite3

def init_db():
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    # Create a table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY,
        date: Optional[str] = None 
        time: Optional[str] = None
        duration: Optional[int] = None
        priority: Optional[str] = None
        importance: Optional[str] = None 
        confidence: Optional[int] = None
        additional_details: Optional[str] = None
        anyone_needed: Optional[str] = None
    )
    ''')
    conn.commit()
    conn.close()

# Run this once to initialize
init_db()
