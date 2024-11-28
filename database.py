import sqlite3

def create_connection():
    conn = sqlite3.connect('pomodoro_sessions.db')
    return conn

def create_tables(conn):
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            start_time TEXT,
            end_time TEXT,
            type TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER,
            task TEXT,
            completed BOOLEAN,
            FOREIGN KEY (session_id) REFERENCES sessions (id)
        )
    ''')
    conn.commit()

def insert_session(conn, start_time, end_time, session_type):
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO sessions (start_time, end_time, type)
        VALUES (?, ?, ?)
    ''', (start_time, end_time, session_type))
    conn.commit()
    return cursor.lastrowid

def insert_task(conn, session_id, task, completed=False):
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO tasks (session_id, task, completed)
        VALUES (?, ?, ?)
    ''', (session_id, task, completed))
    conn.commit()
