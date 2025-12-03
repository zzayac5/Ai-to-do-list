import sqlite3

def init_db():
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    # Create a table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        description TEXT NOT NULL,
        date TEXT,
        time TEXT,
        duration INTEGER,
        priority TEXT,
        importance TEXT,
        confidence INTEGER,
        additional_details TEXT,
        anyone_needed TEXT
    );
    ''')
    conn.commit()
    conn.close()

# Run this once to initialize
init_db()
