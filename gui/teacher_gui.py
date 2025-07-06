import tkinter as tk
from tkinter import ttk, filedialog
from models import (
    add_student, get_students_by_teacher, record_attendance,
    get_student_by_id, get_attendance, update_profile, get_user, add_user
)
from face_utils import capture_face_samples, load_known_faces, recognize_face_and_mark
from gui.common import show_info, show_error, APP_BG, PRIMARY, ACCENT
from auth import hash_password, change_password
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

class TeacherDashboard(ttk.Frame):
    def __init__(self, master, teacher, logout_callback=None):
        super().__init__(master)
        self.master = master
        self.teacher = teacher
        self.logout_callback = logout_callback
        master.title("Teacher Dashboard")
        self.pack(fill="both", expand=1)
        self.build_ui()

    def build_ui(self):
        header = tk.Frame(self, bg=PRIMARY)
        header.pack(side="top", fill="x")
        tk.Label(header, text="Teacher Dashboard", font=('Arial', 24, 'bold'), bg=PRIMARY, fg="white").pack(side="left", padx=30, pady=10)
        if self.logout_callback:
            ttk.Button(header, text="Logout", style="Accent.TButton", command=self.logout).pack(side="right", padx=30, pady=10)
        self.tabs = ttk.Notebook(self)
        self.tabs.pack(fill="both", expand=1, padx=0, pady=0)
        self.student_frame = ttk.Frame(self.tabs)
        self.tabs.add(self.student_frame, text="Students")
        self.attendance_frame = ttk.Frame(self.tabs)
        self.tabs.add(self.attendance_frame, text="Attendance")
        self.profile_frame = ttk.Frame(self.tabs)
        self.tabs.add(self.profile_frame, text="Profile")
        self.setup_students_tab()
        self.setup_attendance_tab()
        self.setup_profile_tab()

    def logout(self):
        if self.logout_callback:
            self.logout_callback()

    def setup_students_tab(self):
        frm = tk.Frame(self.student_frame)
        frm.pack(fill="both", expand=1)
        addfrm = tk.LabelFrame(frm, text="Add Student", font=('Arial', 13, 'bold'))
        addfrm.pack(fill="x", padx=10, pady=10)
        tk.Label(addfrm, text="Name").grid(row=0, column=0, sticky="e")
        self.stud_name = ttk.Entry(addfrm, width=18)
        self.stud_name.grid(row=0, column=1, padx=3)
        tk.Label(addfrm, text="Student ID").grid(row=0, column=2, sticky="e")
        self.stud_id = ttk.Entry(addfrm, width=12)
        self.stud_id.grid(row=0, column=3, padx=3)
        tk.Label(addfrm, text="Email").grid(row=0, column=4, sticky="e")
        self.stud_email = ttk.Entry(addfrm, width=20)
        self.stud_email.grid(row=0, column=5, padx=3)
        tk.Label(addfrm, text="Password").grid(row=0, column=6, sticky="e")
        self.stud_pass = ttk.Entry(addfrm, show="*", width=15)
        self.stud_pass.grid(row=0, column=7, padx=3)
        tk.Label(addfrm, text="Info").grid(row=0, column=8, sticky="e")
        self.stud_info = ttk.Entry(addfrm, width=20)
        self.stud_info.grid(row=0, column=9, padx=3)
        ttk.Button(addfrm, text="Capture Face & Register", style="Accent.TButton", command=self.add_and_capture).grid(row=0, column=10, padx=8)
        
        listfrm = tk.Frame(frm)
        listfrm.pack(fill="both", expand=1)
        self.studlist = ttk.Treeview(listfrm, columns=("ID", "Name", "Email"), show="headings", height=20)
        self.studlist.heading("ID", text="Student ID")
        self.studlist.heading("Name", text="Name")
        self.studlist.heading("Email", text="Email")
        self.studlist.pack(side="left", fill="y", padx=(10,0), pady=10)
        self.studlist.bind("<Double-1>", self.show_student_attendance)
        vsb = ttk.Scrollbar(listfrm, orient="vertical", command=self.studlist.yview)
        self.studlist.configure(yscroll=vsb.set)
        vsb.pack(side="left", fill="y")
        instr = tk.Label(listfrm, text="Double-click a student to see attendance chart, filter, and export options.", font=("Arial", 11, "italic"))
        instr.pack(side="left", padx=25)
        self.refresh_students()

    def add_and_capture(self):
        sid = self.stud_id.get().strip()
        name = self.stud_name.get().strip()
        info = self.stud_info.get().strip()
        email = self.stud_email.get().strip()
        password = self.stud_pass.get().strip()
        if not sid or not name or not email or not password:
            show_error("All fields except info required!")
            return
        if capture_face_samples(sid, num_samples=30):
            try:
                add_student(name, sid, self.teacher[0], f"assets/faces/{sid}", info)
                add_user(sid, hash_password(password), "student", name, email)
                show_info("Student added and faces captured.")
                self.refresh_students()
            except Exception as e:
                show_error(str(e))
        else:
            show_error("Failed to capture enough face samples.")

    def refresh_students(self):
        for i in self.studlist.get_children():
            self.studlist.delete(i)
        for s in get_students_by_teacher(self.teacher[0]):
            user = get_user(str(s[2]))
            email = user[5] if user else ""
            self.studlist.insert("", "end", values=(s[2], s[1], email))

    def show_student_attendance(self, event):
        item = self.studlist.selection()
        if not item:
            return
        values = self.studlist.item(item, "values")
        student_id, name, email = values
        student_db = get_student_by_id(str(student_id))
        if student_db is None:
            show_error("Student not found in the database.")
            return
        records = get_attendance(student_db[0])
        
        def show_chart(period="all"):
            recs = filter_records(records, period)
            present = sum(1 for r in recs if r[1] == "present")
            absent = sum(1 for r in recs if r[1] != "present")
            total = len(recs)
            if total == 0:
                show_error("No records for this period.")
                return
            plt.figure(figsize=(4,4))
            plt.pie([present, absent], labels=["Present", "Absent"], autopct="%1.1f%%", colors=["#5EC576", "#E74C3C"])
            plt.title(f"{name} - {period.title()} (Total: {total})")
            plt.show()
        
        def export_csv(period="all"):
            recs = filter_records(records, period)
            save_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV","*.csv")])
            if save_path:
                with open(save_path, "w", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow(["Date", "Status", "Mode"])
                    for r in recs:
                        writer.writerow(r)
                show_info("Export complete.")
        
        top = tk.Toplevel(self)
        top.title(f"Attendance Report: {name}")
        tk.Label(top, text=f"Attendance Report: {name}", font=("Arial", 15, "bold")).pack(pady=14)
        
        # Show totals
        recs_all = records
        recs_w = filter_records(records, "week")
        recs_m = filter_records(records, "month")
        for lab, recs in [("All Time", recs_all), ("This Week", recs_w), ("This Month", recs_m)]:
            present = sum(1 for r in recs if r[1] == "present")
            absent = sum(1 for r in recs if r[1] != "present")
            total = len(recs)
            tk.Label(top, text=f"{lab}: Present: {present}, Absent: {absent}, Total: {total}", font=("Arial", 12)).pack()
        
        fbtn = tk.Frame(top)
        fbtn.pack(pady=10)
        ttk.Button(fbtn, text="Pie Chart (All)", command=lambda: show_chart("all")).pack(side="left", padx=6)
        ttk.Button(fbtn, text="Pie Chart (Week)", command=lambda: show_chart("week")).pack(side="left", padx=6)
        ttk.Button(fbtn, text="Pie Chart (Month)", command=lambda: show_chart("month")).pack(side="left", padx=6)
        ttk.Button(fbtn, text="Export All (CSV)", command=lambda: export_csv("all")).pack(side="left", padx=6)
        ttk.Button(fbtn, text="Export Week (CSV)", command=lambda: export_csv("week")).pack(side="left", padx=6)
        ttk.Button(fbtn, text="Export Month (CSV)", command=lambda: export_csv("month")).pack(side="left", padx=6)

    def setup_attendance_tab(self):
        frm = tk.Frame(self.attendance_frame)
        frm.pack(fill="both", expand=1)
        tk.Label(frm, text="Date (YYYY-MM-DD):", font=("Arial", 12, "bold")).pack(side="left", padx=10, pady=10)
        self.date_entry = ttk.Entry(frm, font=("Arial", 12), width=15)
        today_str = datetime.now().strftime("%Y-%m-%d")
        self.date_entry.insert(0, today_str)
        self.date_entry.pack(side="left", padx=5, pady=10)
        ttk.Button(frm, text="Start Attendance by Face", style="Accent.TButton", command=self.start_attendance_by_face).pack(side="left", padx=12)
        
        self.attendance_tree = ttk.Treeview(frm, columns=("ID", "Name", "Status"), show="headings", height=18)
        self.attendance_tree.heading("ID", text="Student ID")
        self.attendance_tree.heading("Name", text="Name")
        self.attendance_tree.heading("Status", text="Status")
        self.attendance_tree.pack(fill="both", expand=1, pady=(50,10), padx=10)
        self.refresh_attendance_list()

    def refresh_attendance_list(self):
        for i in self.attendance_tree.get_children():
            self.attendance_tree.delete(i)
        date_str = self.date_entry.get().strip()
        students = get_students_by_teacher(self.teacher[0])
        for s in students:
            status = "Absent"
            records = get_attendance(s[0])
            for rec in records:
                if rec[0] == date_str and rec[1] == "present":
                    status = "Present"
            self.attendance_tree.insert("", "end", values=(s[2], s[1], status))

    def start_attendance_by_face(self):
        date_str = self.date_entry.get().strip()
        if not date_str:
            show_error("Please enter a date.")
            return
        
        students = get_students_by_teacher(self.teacher[0])
        already_marked = set()
        for s in students:
            records = get_attendance(s[0])
            for rec in records:
                if rec[0] == date_str and rec[1] == "present":
                    already_marked.add(str(s[2]))
        
        known_encs, student_ids = load_known_faces()
        if not known_encs:
            show_error("No student faces found. Please register students first.")
            return

        def on_recognized(student_id):
            for s in students:
                if str(s[2]) == str(student_id):
                    record_attendance(s[0], date_str, "present", "face")
                    show_info(f"Attendance marked: {s[1]} ({student_id})")
                    break

        stop_flag = [False]
        def stop_callback():
            return stop_flag[0]
        
        recognize_face_and_mark(known_encs, student_ids, already_marked, on_recognized, stop_callback)
        self.refresh_attendance_list()

    def setup_profile_tab(self):
        frm = tk.Frame(self.profile_frame)
        frm.pack(fill="both", expand=1, padx=80, pady=50)
        pf = tk.LabelFrame(frm, text="Profile", font=('Arial', 13, 'bold'))
        pf.pack(fill="x", padx=10, pady=10)
        tk.Label(pf, text="Name").grid(row=0, column=0, sticky="e", pady=8)
        self.profile_name = ttk.Entry(pf)
        self.profile_name.insert(0, self.teacher[4])
        self.profile_name.grid(row=0, column=1, pady=8)
        tk.Label(pf, text="Email").grid(row=1, column=0, sticky="e", pady=8)
        self.profile_email = ttk.Entry(pf)
        self.profile_email.insert(0, self.teacher[5])
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
        update_profile(self.teacher[1], name, email)
        show_info("Profile updated.")

    def change_password(self):
        old = self.oldpass.get().strip()
        new = self.newpass.get().strip()
        if not old or not new:
            show_error("Both fields required.")
            return
        if change_password(self.teacher[1], old, new):
            show_info("Password changed.")
        else:
            show_error("Old password incorrect.")