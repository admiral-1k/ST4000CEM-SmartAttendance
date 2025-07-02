import tkinter as tk
from tkinter import ttk
from gui.login_gui import LoginFrame, RegisterFrame
from gui.admin_gui import AdminDashboard
from gui.teacher_gui import TeacherDashboard
from gui.student_gui import StudentDashboard
from models import get_user

def set_style():
    style = ttk.Style()
    try:
        style.theme_use('clam')
    except:
        pass
    style.configure("Accent.TButton",
                    font=("Arial", 13, "bold"),
                    background="#5EC576",
                    foreground="#fff",
                    borderwidth=0,
                    focusthickness=3,
                    focuscolor='none',
                    padding=8)
    style.map("Accent.TButton",
              background=[("active", "#3B5998")],
              foreground=[("active", "#fff")])
    style.configure("TNotebook.Tab", font=("Arial", 13, "bold"))
    style.configure("Treeview.Heading", font=("Arial", 12, "bold"))

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Smart Attendance System")
        self.geometry("1200x700")
        self.resizable(False, False)
        set_style()
        self.show_login()

    def clear_frame(self):
        for widget in self.winfo_children():
            widget.destroy()

    def show_login(self):
        self.clear_frame()
        self.curr_frame = LoginFrame(
            self, 
            on_login=self.start_dashboard, 
            on_register=self.show_register
        )
        self.curr_frame.pack(fill="both", expand=1)

    def show_register(self):
        self.clear_frame()
        self.curr_frame = RegisterFrame(
            self, 
            on_register_success=self.show_login, 
            on_back=self.show_login
        )
        self.curr_frame.pack(fill="both", expand=1)

    def start_dashboard(self, user):
        self.clear_frame()
        def logout():
            self.show_login()
        if user[3] == "admin":
            AdminDashboard(self, user, logout_callback=logout)
        elif user[3] == "teacher":
            TeacherDashboard(self, user, logout_callback=logout)
        elif user[3] == "student":
            StudentDashboard(self, user, logout_callback=logout)

if __name__ == "__main__":
    App().mainloop()