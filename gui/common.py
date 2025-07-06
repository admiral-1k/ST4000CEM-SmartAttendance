import tkinter as tk
from tkinter import messagebox

APP_BG = "#F3F6FB"
PRIMARY = "#3B5998"
ACCENT = "#5EC576"
ERROR = "#E74C3C"
DARK = "#273043"

def center_window(window, width=1200, height=700):
    ws = window.winfo_screenwidth()
    hs = window.winfo_screenheight()
    x = (ws/2) - (width/2)
    y = (hs/2) - (height/2)
    window.geometry(f'{width}x{height}+{int(x)}+{int(y)}')

def show_info(msg):
    messagebox.showinfo("Info", msg)

def show_error(msg):
    messagebox.showerror("Error", msg)

def style_heading(widget):
    widget.config(font=('Arial', 22, 'bold'), bg=APP_BG, fg=PRIMARY)