import matplotlib.pyplot as plt

def plot_attendance(attendance_records, student_name):
    dates = [rec[0] for rec in attendance_records]
    statuses = [1 if rec[1] == 'present' else 0 for rec in attendance_records]
    plt.figure(figsize=(8,4))
    plt.plot(dates, statuses, marker='o')
    plt.title(f"Attendance Chart for {student_name}")
    plt.ylabel("Present (1) / Absent (0)")
    plt.xlabel("Date")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()