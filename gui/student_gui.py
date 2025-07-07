import tkinter as tk
from tkinter import ttk, filedialog
from models import get_attendance, update_profile
from gui.common import show_info, show_error, APP_BG, PRIMARY
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import csv

def filter_records(records, period="all"):
    now = datetime.now()
    if period == "week":
        from_date = now - timedelta(days=7)
    elif period == "month":
        from_date = now - timedelta(days=30)
    else:
        return records
    return [r for r in records if datetime.strptime(r[0], "%Y-%m-%d") >= from_date]

class StudentDashboard(ttk.Frame):
    def __init__(self, master, student, logout_callback=None):
        super().__init__(master)
        self.master = master
        self.student = student
        self.logout_callback = logout_callback
        self.pack(fill="both", expand=1)
        master.title("Student Dashboard")
        self.build_ui()

    def build_ui(self):
        header = tk.Frame(self, bg=PRIMARY)
        header.pack(side="top", fill="x")
        ttk.Label(header, text=f"Student Dashboard", font=('Arial', 18, 'bold')).pack(side="left", padx=30, pady=10)
        if self.logout_callback:
            ttk.Button(header, text="Logout", style="Accent.TButton", command=self.logout).pack(side="right", padx=30, pady=10)
        
        self.tabs = ttk.Notebook(self)
        self.tabs.pack(fill="both", expand=1, padx=0, pady=0)
        self.attendance_frame = ttk.Frame(self.tabs)
        self.tabs.add(self.attendance_frame, text="Attendance")
        self.profile_frame = ttk.Frame(self.tabs)
        self.tabs.add(self.profile_frame, text="Profile")
        
        self.setup_attendance_tab()
        self.setup_profile_tab()

    def logout(self):
        if self.logout_callback:
            self.logout_callback()

    def setup_attendance_tab(self):
        frm = tk.Frame(self.attendance_frame)
        frm.pack(fill="both", expand=1, padx=60, pady=40)
        
        self.period_var = tk.StringVar(value="all")
        periods = [("All Time", "all"), ("This Week", "week"), ("This Month", "month")]
        for txt, val in periods:
            ttk.Radiobutton(frm, text=txt, variable=self.period_var, value=val).pack(side="left", padx=10)
        
        ttk.Button(frm, text="View Attendance Chart", style="Accent.TButton", command=self.show_chart).pack(pady=18, ipadx=18, ipady=4)
        ttk.Button(frm, text="Export Attendance Report", style="Accent.TButton", command=self.save_report).pack(pady=8, ipadx=18, ipady=4)
        
        self.info_label = tk.Label(frm, text="", font=("Arial",12))
        self.info_label.pack(pady=10)
        self.update_info()

    def update_info(self):
        records = get_attendance(self.student[0])
        period = self.period_var.get()
        recs = filter_records(records, period)
        present = sum(1 for r in recs if r[1] == "present")
        absent = sum(1 for r in recs if r[1] != "present")
        total = len(recs)
        self.info_label.config(text=f"Present: {present}, Absent: {absent}, Total: {total}")

    def show_chart(self):
        records = get_attendance(self.student[0])
        period = self.period_var.get()
        recs = filter_records(records, period)
        present = sum(1 for r in recs if r[1] == "present")
        absent = sum(1 for r in recs if r[1] != "present")
        total = len(recs)
        self.update_info()
        
        if total == 0:
            show_error("No attendance data for this period.")
            return
        
        plt.figure(figsize=(4,4))
        plt.pie([present, absent], labels=["Present", "Absent"], autopct="%1.1f%%", colors=["#5EC576", "#E74C3C"])
        plt.title(f"Attendance ({period.title()}) - Total: {total}")
        plt.show()

    def save_report(self):
        records = get_attendance(self.student[0])
        period = self.period_var.get()
        recs = filter_records(records, period)
        
        if not recs:
            show_error("No attendance data to export for this period.")
            return
            
        save_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV","*.csv")])
        if save_path:
            with open(save_path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Date", "Status", "Mode"])
                for r in recs:
                    writer.writerow(r)
            show_info(f"Report saved as {save_path}.")

    def setup_profile_tab(self):
        frm = tk.Frame(self.profile_frame)
        frm.pack(fill="both", expand=1, padx=80, pady=50)
        pf = tk.LabelFrame(frm, text="Profile", font=('Arial', 13, 'bold'))
        pf.pack(fill="x", padx=10, pady=10)
        tk.Label(pf, text="Name").grid(row=0, column=0, sticky="e", pady=8)
        self.profile_name = ttk.Entry(pf)
        self.profile_name.insert(0, self.student[4])
        self.profile_name.grid(row=0, column=1, pady=8)
        tk.Label(pf, text="Email").grid(row=1, column=0, sticky="e", pady=8)
        self.profile_email = ttk.Entry(pf)
        self.profile_email.insert(0, self.student[5])
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
        update_profile(self.student[1], name, email)
        show_info("Profile updated.")

    def change_password(self):
        old = self.oldpass.get().strip()
        new = self.newpass.get().strip()
        if not old or not new:
            show_error("Both fields required.")
            return
        from auth import change_password
        if change_password(self.student[1], old, new):
            show_info("Password changed.")
        else:
            show_error("Old password incorrect.")