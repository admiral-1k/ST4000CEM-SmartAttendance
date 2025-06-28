import tkinter as tk
from tkinter import ttk
import re
from auth import hash_password, verify_password, forgot_password
from models import get_user, add_user
from gui.common import center_window, show_error, show_info, APP_BG, PRIMARY, DARK, ACCENT, ERROR

def validate_email(email):
    return re.match(r"^[^@]+@[^@]+\.[^@]+$", email)

class LoginFrame(tk.Frame):
    def __init__(self, master, on_login, on_register):
        super().__init__(master, bg=APP_BG)
        self.on_login = on_login
        self.on_register = on_register
        self.build_ui()

    def build_ui(self):
        left = tk.Frame(self, bg=PRIMARY, width=500)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)
        tk.Label(left, text="Smart Attendance\nSystem", font=("Arial", 36, "bold"),
                 bg=PRIMARY, fg="white", justify="center").place(relx=0.5, rely=0.4, anchor="center")
        tk.Label(left, text="AI-powered face & manual attendance\nModern Admin Panel",
                 font=("Arial", 15), bg=PRIMARY, fg=ACCENT, justify="center").place(relx=0.5, rely=0.6, anchor="center")

        right = tk.Frame(self, bg=APP_BG)
        right.pack(side="right", fill="both", expand=1)

        card = tk.Frame(right, bg="white", bd=2, relief="groove")
        card.place(relx=0.5, rely=0.5, anchor="center", width=440, height=480)

        tk.Label(card, text="Sign In", font=("Arial", 22, "bold"), bg="white", fg=PRIMARY).pack(pady=(36,10))

        form = tk.Frame(card, bg="white")
        form.pack(padx=30, pady=10, fill="x")

        tk.Label(form, text="Username", bg="white", anchor="w", font=("Arial", 12, "bold")).pack(fill="x")
        self.username = ttk.Entry(form, font=("Arial", 13))
        self.username.pack(pady=(0,8), fill="x")

        tk.Label(form, text="Password", bg="white", anchor="w", font=("Arial", 12, "bold")).pack(fill="x")
        self.password = ttk.Entry(form, show="*", font=("Arial", 13))
        self.password.pack(pady=(0,8), fill="x")

        tk.Label(form, text="Role", bg="white", anchor="w", font=("Arial", 12, "bold")).pack(fill="x")
        self.role = tk.StringVar(value="admin")
        roles = tk.Frame(form, bg="white")
        roles.pack(pady=(2,10), anchor="w")
        for r in ['admin', 'teacher', 'student']:
            ttk.Radiobutton(roles, text=r.capitalize(), variable=self.role, value=r).pack(side="left", padx=12)

        ttk.Button(card, text="Login", style="Accent.TButton", command=self.try_login).pack(pady=(18,7), fill="x", padx=60)
        tk.Button(card, text="Forgot Password?", fg=PRIMARY, bg="white", bd=0, font=("Arial", 11, "underline"), command=self.forgot).pack(pady=2)
        tk.Label(card, text="Don't have an account?", bg="white", fg=DARK).pack(pady=(34,1))
        tk.Button(card, text="Register", command=self.on_register, bg="white", fg=ACCENT, font=("Arial", 13, "underline"), bd=0).pack()

    def try_login(self):
        username = self.username.get().strip()
        password = self.password.get().strip()
        role = self.role.get()
        user = get_user(username)
        if not user or user[3] != role:
            show_error("User/role not found!\nTry admin/admin123 for the default admin.")
            return
        if verify_password(password, user[2]):
            self.on_login(user)
        else:
            show_error("Incorrect password!")

    def forgot(self):
        ForgotPasswordPopup(self.master)

class RegisterFrame(tk.Frame):
    def __init__(self, master, on_register_success, on_back):
        super().__init__(master, bg=APP_BG)
        self.on_register_success = on_register_success
        self.on_back = on_back
        self.build_ui()

    def build_ui(self):
        left = tk.Frame(self, bg=ACCENT, width=500)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)
        tk.Label(left, text="Create Account", font=("Arial", 30, "bold"), bg=ACCENT, fg="white", justify="center").place(relx=0.5, rely=0.4, anchor="center")
        tk.Label(left, text="Register as Student or Teacher", font=("Arial", 15), bg=ACCENT, fg=DARK, justify="center").place(relx=0.5, rely=0.6, anchor="center")

        right = tk.Frame(self, bg=APP_BG)
        right.pack(side="right", fill="both", expand=1)
        card = tk.Frame(right, bg="white", bd=2, relief="groove")
        card.place(relx=0.5, rely=0.5, anchor="center", width=440, height=560)
        tk.Label(card, text="Register", font=("Arial", 22, "bold"), bg="white", fg=ACCENT).pack(pady=(36,15))

        form = tk.Frame(card, bg="white")
        form.pack(padx=30, pady=10, fill="x")

        tk.Label(form, text="Full Name", bg="white", anchor="w", font=("Arial", 12, "bold")).pack(fill="x")
        self.name = ttk.Entry(form, font=("Arial", 13))
        self.name.pack(pady=(0,7), fill="x")

        tk.Label(form, text="Username", bg="white", anchor="w", font=("Arial", 12, "bold")).pack(fill="x")
        self.username = ttk.Entry(form, font=("Arial", 13))
        self.username.pack(pady=(0,7), fill="x")

        tk.Label(form, text="Email", bg="white", anchor="w", font=("Arial", 12, "bold")).pack(fill="x")
        self.email = ttk.Entry(form, font=("Arial", 13))
        self.email.pack(pady=(0,7), fill="x")

        tk.Label(form, text="Password", bg="white", anchor="w", font=("Arial", 12, "bold")).pack(fill="x")
        self.password = ttk.Entry(form, show="*", font=("Arial", 13))
        self.password.pack(pady=(0,7), fill="x")

        tk.Label(form, text="Role", bg="white", anchor="w", font=("Arial", 12, "bold")).pack(fill="x")
        self.role = tk.StringVar(value="student")
        roles = tk.Frame(form, bg="white")
        roles.pack(pady=(2,12), anchor="w")
        for r in ['student', 'teacher']:
            ttk.Radiobutton(roles, text=r.capitalize(), variable=self.role, value=r).pack(side="left", padx=20)

        ttk.Button(card, text="Register", style="Accent.TButton", command=self.try_register).pack(pady=(17,12), fill="x", padx=60)
        tk.Button(card, text="Back to Login", bg="white", fg=ACCENT, bd=0, font=("Arial", 12, "underline"), command=self.on_back).pack()

    def try_register(self):
        name = self.name.get().strip()
        username = self.username.get().strip()
        email = self.email.get().strip()
        password = self.password.get().strip()
        role = self.role.get()
        if not name or not username or not email or not password or not role:
            show_error("All fields are required.")
            return
        if not validate_email(email):
            show_error("Enter a valid email address.")
            return
        try:
            add_user(username, hash_password(password), role, name, email)
            show_info("Registration successful!")
            self.on_register_success()
        except Exception as e:
            show_error(str(e))

class ForgotPasswordPopup:
    def __init__(self, master):
        self.top = tk.Toplevel(master)
        self.top.title("Forgot Password")
        self.top.configure(bg=APP_BG)
        center_window(self.top, 420, 340)
        self.top.resizable(False, False)
        card = tk.Frame(self.top, bg="white", bd=2, relief="groove")
        card.place(relx=0.5, rely=0.5, anchor="center", width=360, height=270)
        tk.Label(card, text="Forgot Password", font=("Arial", 18, "bold"), bg="white", fg=ERROR).pack(pady=(18,9))
        tk.Label(card, text="Username", bg="white", font=("Arial", 12, "bold")).pack()
        self.ent_user = ttk.Entry(card)
        self.ent_user.pack(pady=(0,8), fill="x", padx=30)
        tk.Label(card, text="Email", bg="white", font=("Arial", 12, "bold")).pack()
        self.ent_email = ttk.Entry(card)
        self.ent_email.pack(pady=(0,8), fill="x", padx=30)
        tk.Label(card, text="New Password", bg="white", font=("Arial", 12, "bold")).pack()
        self.ent_new = ttk.Entry(card, show="*")
        self.ent_new.pack(pady=(0,8), fill="x", padx=30)
        ttk.Button(card, text="Reset", style="Accent.TButton", command=self.do_reset).pack(pady=18, fill="x", padx=70)

    def do_reset(self):
        if forgot_password(self.ent_user.get(), self.ent_email.get(), self.ent_new.get()):
            show_info("Password reset successful.")
            self.top.destroy()
        else:
            show_error("Reset failed. Check username and email.")