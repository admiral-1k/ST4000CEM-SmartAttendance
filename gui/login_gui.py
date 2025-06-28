import tkinter as tk
from tkinter import ttk
import re


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

