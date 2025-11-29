import sqlite3

def init_db():
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    # Create a table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY,
        description TEXT,
        priority INTEGER,
        importance TEXT,
        duration INTEGER,
        confidence INTEGER,
        due_date TEXT
    )
    ''')
    conn.commit()
    conn.close()

# Run this once to initialize
init_db()
