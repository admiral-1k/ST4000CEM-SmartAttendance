# File: models.py
from db import get_connection

def get_user(username):
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=?", (username,))
        return c.fetchone()
