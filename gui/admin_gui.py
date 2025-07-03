import tkinter as tk
from tkinter import ttk, filedialog
from models import (
    get_all_teachers, get_all_students, get_user,
    update_profile, add_user, get_students_by_teacher
)
from gui.common import show_info, show_error, APP_BG, PRIMARY, ACCENT
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import csv

def get_role_count(role):
    from db import get_connection
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM users WHERE role=?", (role,))
        return c.fetchone()[0]

def get_attendance_summary():
    from db import get_connection
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT date, COUNT(*) FROM attendance WHERE status='present' GROUP BY date")
        return dict(c.fetchall())

def get_all_attendance_records():
    from db import get_connection
    with get_connection() as conn:
        c = conn.cursor()
        c.execute(
            "SELECT s.student_id, s.name, a.date, a.status, a.mode FROM attendance a "
            "JOIN students s ON a.student_id=s.id"
        )
        return c.fetchall()

class AdminDashboard(ttk.Frame):
    def __init__(self, master, admin, logout_callback=None):
        super().__init__(master)
        self.master = master
        self.admin = admin
        self.logout_callback = logout_callback
        self.pack(fill="both", expand=1)
        master.title("Admin Dashboard")
        self.build_ui()

    def build_ui(self):
        header = tk.Frame(self, bg=PRIMARY)
        header.pack(side="top", fill="x")
        tk.Label(header, text="Admin Dashboard", font=('Arial', 26, 'bold'), bg=PRIMARY, fg="white").pack(side="left", padx=30, pady=10)
        if self.logout_callback:
            ttk.Button(header, text="Logout", style="Accent.TButton", command=self.logout).pack(side="right", padx=30, pady=10)

        self.tabs = ttk.Notebook(self)
        self.tabs.pack(fill="both", expand=1, padx=0, pady=0)
        self.dashboard_frame = ttk.Frame(self.tabs)
        self.tabs.add(self.dashboard_frame, text="Dashboard")
        self.teachers_frame = ttk.Frame(self.tabs)
        self.tabs.add(self.teachers_frame, text="Teachers")
        self.students_frame = ttk.Frame(self.tabs)
        self.tabs.add(self.students_frame, text="Students")
        self.profile_frame = ttk.Frame(self.tabs)
        self.tabs.add(self.profile_frame, text="Profile")

        self.setup_dashboard_tab()
        self.setup_teachers_tab()
        self.setup_students_tab()
        self.setup_profile_tab()

    def logout(self):
        if self.logout_callback:
            self.logout_callback()

    def setup_dashboard_tab(self):
        f = tk.Frame(self.dashboard_frame)
        f.pack(fill="both", expand=1)
        cardf = tk.Frame(f, bg=APP_BG)
        cardf.pack(pady=20, fill="x")
        for i, (label, color, getter) in enumerate([
            ("Admins", PRIMARY, lambda: get_role_count("admin")),
            ("Teachers", ACCENT, lambda: get_role_count("teacher")),
            ("Students", "#E67E22", lambda: get_role_count("student"))
        ]):
            val = getter()
            card = tk.Frame(cardf, bg=color, width=180, height=60)
            card.pack(side="left", padx=25, fill="x", expand=1)
            tk.Label(card, text=label, font=('Arial', 16, 'bold'), bg=color, fg="white").pack()
            tk.Label(card, text=str(val), font=('Arial', 20, 'bold'), bg=color, fg="white").pack()
        
        actionf = tk.Frame(f, bg=APP_BG)
        actionf.pack(fill="both", expand=1, pady=20)
        tk.Label(actionf, text="Attendance Report (Total Present/Day)", font=('Arial', 15, 'bold'), bg=APP_BG, fg=PRIMARY).pack()
        summary = get_attendance_summary()
        if summary:
            dates = sorted(summary.keys())
            values = [summary[d] for d in dates]
            fig, ax = plt.subplots(figsize=(7, 2.3), dpi=100)
            ax.bar(dates, values, color=ACCENT)
            ax.set_xlabel("Date")
            ax.set_ylabel("Present")
            ax.set_title("Attendance per Day")
            plt.xticks(rotation=45)
            fig.tight_layout()
            canvas = FigureCanvasTkAgg(fig, master=actionf)
            canvas.get_tk_widget().pack()
            canvas.draw()
        else:
            tk.Label(actionf, text="No attendance data.", bg=APP_BG, fg="gray").pack()
        expf = tk.Frame(actionf, bg=APP_BG)
        expf.pack(pady=15)
        ttk.Button(expf, text="Export All Attendance (CSV)", command=self.export_attendance).pack(side="left", padx=6)
        ttk.Button(expf, text="Show Pie Chart (All Students)", command=self.show_pie_chart).pack(side="left", padx=6)

    def export_attendance(self):
        records = get_all_attendance_records()
        if not records:
            show_error("No attendance data to export.")
            return
        save_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV","*.csv")])
        if save_path:
            with open(save_path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["StudentID", "Name", "Date", "Status", "Mode"])
                for r in records:
                    writer.writerow(r)
            show_info(f"Exported as {save_path}")

    def show_pie_chart(self):
        records = get_all_attendance_records()
        if not records:
            show_error("No attendance data.")
            return
        present = sum(1 for r in records if r[3] == "present")
        absent = sum(1 for r in records if r[3] != "present")
        plt.figure(figsize=(4,4))
        plt.pie([present, absent], labels=["Present", "Absent"], autopct="%1.1f%%", colors=["#5EC576", "#E74C3C"])
        plt.title("All Students Attendance")
        plt.show()

    def setup_teachers_tab(self):
        f = tk.Frame(self.teachers_frame)
        f.pack(fill="both", expand=1)
        addf = tk.LabelFrame(f, text="Add Teacher", font=('Arial', 13, 'bold'))
        addf.pack(fill="x", padx=10, pady=12)
        tk.Label(addf, text="Name").grid(row=0, column=0, sticky="e")
        self.tch_name = ttk.Entry(addf, width=18)
        self.tch_name.grid(row=0, column=1, padx=3)
        tk.Label(addf, text="Username").grid(row=0, column=2, sticky="e")
        self.tch_uname = ttk.Entry(addf, width=15)
        self.tch_uname.grid(row=0, column=3, padx=3)
        tk.Label(addf, text="Email").grid(row=0, column=4, sticky="e")
        self.tch_email = ttk.Entry(addf, width=20)
        self.tch_email.grid(row=0, column=5, padx=3)
        tk.Label(addf, text="Password").grid(row=0, column=6, sticky="e")
        self.tch_pass = ttk.Entry(addf, show="*", width=15)
        self.tch_pass.grid(row=0, column=7, padx=3)
        ttk.Button(addf, text="Add Teacher", style="Accent.TButton", command=self.add_teacher).grid(row=0, column=8, padx=8)
        
        listf = tk.Frame(f)
        listf.pack(fill="x", padx=10, pady=16)
        self.tch_tree = ttk.Treeview(listf, columns=("ID", "Name", "Username", "Email"), show="headings", height=10)
        for col in ("ID", "Name", "Username", "Email"):
            self.tch_tree.heading(col, text=col)
        self.tch_tree.pack(fill="x")
        self.refresh_teachers()

    def add_teacher(self):
        name = self.tch_name.get().strip()
        uname = self.tch_uname.get().strip()
        email = self.tch_email.get().strip()
        password = self.tch_pass.get().strip()
        if not name or not uname or not email or not password:
            show_error("All fields required!")
            return
        try:
            add_user(uname, password, "teacher", name, email)
            show_info("Teacher added.")
            self.refresh_teachers()
        except Exception as e:
            show_error(str(e))

    def refresh_teachers(self):
        for i in self.tch_tree.get_children():
            self.tch_tree.delete(i)
        for t in get_all_teachers():
            self.tch_tree.insert("", "end", values=(t[0], t[4], t[1], t[5]))

    def setup_students_tab(self):
        f = tk.Frame(self.students_frame)
        f.pack(fill="both", expand=1)
        
        # Teacher selection
        tk.Label(f, text="Select Teacher:", font=('Arial', 12)).pack(pady=5)
        self.teacher_var = tk.StringVar()
        teachers = get_all_teachers()
        self.teacher_dropdown = ttk.Combobox(f, textvariable=self.teacher_var, 
                                           values=[f"{t[4]} (ID: {t[0]})" for t in teachers])
        self.teacher_dropdown.pack(pady=5)
        self.teacher_dropdown.bind("<<ComboboxSelected>>", self.load_students_for_teacher)
        
        # Student list
        self.student_tree = ttk.Treeview(f, columns=("ID", "Name", "StudentID", "Info"), show="headings", height=15)
        for col in ("ID", "Name", "StudentID", "Info"):
            self.student_tree.heading(col, text=col)
        self.student_tree.pack(fill="both", expand=1, padx=10, pady=10)
        
        # Export button
        ttk.Button(f, text="Export Students (CSV)", command=self.export_students).pack(pady=10)

    def load_students_for_teacher(self, event=None):
        teacher_str = self.teacher_var.get()
        if not teacher_str:
            return
        teacher_id = int(teacher_str.split("ID: ")[1].rstrip(")"))
        
        for i in self.student_tree.get_children():
            self.student_tree.delete(i)
            
        students = get_students_by_teacher(teacher_id)
        for s in students:
            self.student_tree.insert("", "end", values=(s[0], s[1], s[2], s[5]))

    def export_students(self):
        teacher_str = self.teacher_var.get()
        if not teacher_str:
            show_error("Please select a teacher first.")
            return
            
        teacher_id = int(teacher_str.split("ID: ")[1].rstrip(")"))
        students = get_students_by_teacher(teacher_id)
        
        if not students:
            show_error("No students found for this teacher.")
            return
            
        save_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV","*.csv")])
        if save_path:
            with open(save_path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["ID", "Name", "StudentID", "Info"])
                for s in students:
                    writer.writerow([s[0], s[1], s[2], s[5]])
            show_info(f"Exported as {save_path}")

    def setup_profile_tab(self):
        frm = tk.Frame(self.profile_frame)
        frm.pack(fill="both", expand=1, padx=80, pady=50)
        pf = tk.LabelFrame(frm, text="Profile", font=('Arial', 13, 'bold'))
        pf.pack(fill="x", padx=10, pady=10)
        tk.Label(pf, text="Name").grid(row=0, column=0, sticky="e", pady=8)
        self.profile_name = ttk.Entry(pf)
        self.profile_name.insert(0, self.admin[4])
        self.profile_name.grid(row=0, column=1, pady=8)
        tk.Label(pf, text="Email").grid(row=1, column=0, sticky="e", pady=8)
        self.profile_email = ttk.Entry(pf)
        self.profile_email.insert(0, self.admin[5])
        self.profile_email.grid(row=1, column=1, pady=8)
        ttk.Button(pf, text="Update Profile", command=self.update_profile).grid(row=0, column=2, rowspan=2, padx=18)
        pwf = tk.LabelFrame(frm, text="Change Password", font=('Arial', 13, 'bold'))
        pwf.pack(fill="x", padx=10, pady=14)
        tk.Label(pwf, text="Old Password").grid(row=0, column=0, sticky="e", pady=8)
        self.oldpass = ttk.Entry(pwf, show="*")
        self.oldpass.grid(row=0, column=1, pady=8)
        tk.Label(pwf, text="New Password").grid(row=1, column=0, sticky="e", pady=8)
        self.newpass = ttk.Entry(pwf, show="*")
        self.newpass.grid(row=1, column=1, pady=8)
        ttk.Button(pwf, text="Change Password", command=self.change_password).grid(row=0, column=2, rowspan=2, padx=18)

    def update_profile(self):
        name = self.profile_name.get().strip()
        email = self.profile_email.get().strip()
        if not name or not email:
            show_error("Both fields required.")
            return
        update_profile(self.admin[1], name, email)
        show_info("Profile updated.")

    def change_password(self):
        old = self.oldpass.get().strip()
        new = self.newpass.get().strip()
        if not old or not new:
            show_error("Both fields required.")
            return
        from auth import change_password
        if change_password(self.admin[1], old, new):
            show_info("Password changed.")
        else:
            show_error("Old password incorrect.")