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

def get_attendance(student_id):
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT date, status, mode FROM attendance WHERE student_id=?", (student_id,))
        return c.fetchall()

def get_students_by_teacher(teacher_id):
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM students WHERE teacher_id=?", (teacher_id,))
        return c.fetchall()

def get_all_teachers():
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE role='teacher'")
        return c.fetchall()

def get_all_students():
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM students")
        return c.fetchall()

def get_attendance_by_teacher(teacher_id):
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("""
        SELECT students.name, attendance.date, attendance.status
        FROM attendance
        JOIN students ON attendance.student_id = students.id
        WHERE students.teacher_id=?
        """, (teacher_id,))
        return c.fetchall()

def get_teacher_by_id(teacher_id):
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE id=? AND role='teacher'", (teacher_id,))
        return c.fetchone()