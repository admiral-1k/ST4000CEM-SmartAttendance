import hashlib
import random
import string
from models import get_user, update_password, update_profile

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(raw, hashed):
    return hash_password(raw) == hashed

def change_password(username, old, new):
    user = get_user(username)
    if user and verify_password(old, user[2]):
        update_password(username, hash_password(new))
        return True
    return False

def forgot_password(username, email, new_pass):
    user = get_user(username)
    if user and user[5] == email:
        update_password(username, hash_password(new_pass))
        return True
    return False

def generate_temp_password(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def change_profile(username, name, email):
    update_profile(username, name, email)