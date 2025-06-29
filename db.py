import sqlite3
import os
import hashlib

DB_FILE = 'attendance.db'

def get_connection():
    return sqlite3.connect(DB_FILE)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    with get_connection() as conn:
        c = conn.cursor()
        c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT,
            name TEXT,
            email TEXT
        )
        ''')
        c.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            student_id TEXT UNIQUE,
            teacher_id INTEGER,
            photo_path TEXT,
            info TEXT,
            FOREIGN KEY(teacher_id) REFERENCES users(id)
        )
        ''')

        conn.commit()

def ensure_admin():
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username='admin'")
        if not c.fetchone():
            c.execute(
                "INSERT INTO users (username, password, role, name, email) VALUES (?, ?, ?, ?, ?)",
                ("admin", hash_password("admin123"), "admin", "Administrator", "admin@admin.com")
            )
            conn.commit()

if not os.path.exists(DB_FILE):
    init_db()
ensure_admin()