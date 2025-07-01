# File: models.py
from db import get_connection

def get_user(username):
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=?", (username,))
        return c.fetchone()
def get_user_by_id(user_id):
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE id=?", (user_id,))
        return c.fetchone()

def add_user(username, password, role, name, email):
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password, role, name, email) VALUES (?, ?, ?, ?, ?)",
                  (username, password, role, name, email))
        conn.commit()

def update_password(username, new_password):
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("UPDATE users SET password=? WHERE username=?", (new_password, username))
        conn.commit()
def update_profile(username, name, email):
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("UPDATE users SET name=?, email=? WHERE username=?", (name, email, username))
        conn.commit()

def add_student(name, student_id, teacher_id, photo_path, info):
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("INSERT INTO students (name, student_id, teacher_id, photo_path, info) VALUES (?, ?, ?, ?, ?)",
                  (name, student_id, teacher_id, photo_path, info))
        conn.commit()

def get_student_by_id(student_id):
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM students WHERE student_id=?", (str(student_id),))
        return c.fetchone()

def record_attendance(student_id, date, status, mode):
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("INSERT INTO attendance (student_id, date, status, mode) VALUES (?, ?, ?, ?)",
                  (student_id, date, status, mode))
        conn.commit()
