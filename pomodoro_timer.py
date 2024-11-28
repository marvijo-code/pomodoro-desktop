import tkinter as tk
from tkinter import messagebox, ttk
import time
import sqlite3
from database import create_connection, create_tables, insert_session, insert_task
from playsound import playsound

class PomodoroTimer:
    def position_window(self):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.window_width = 400
        self.window_height = 300
        x = screen_width - self.window_width
        y = screen_height - self.window_height - 50  # Adjust y position to start a bit higher
        self.root.geometry(f"{self.window_width}x{self.window_height}+{x}+{y}")

        self.work_time = 25 * 60  # 25 minutes
        self.break_time = 5 * 60  # 5 minutes
        self.timer_running = False
        self.current_time = self.work_time

        self.time_label = tk.Label(root, text=self.format_time(self.current_time), font=("Helvetica", 48), bg="#2c2c2c", fg="white")
        self.time_label.pack(pady=20)

        self.progress_bar = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
        self.progress_bar.pack(pady=10)

        self.button_frame = tk.Frame(root)
        self.button_frame.pack(pady=5)

        self.start_button = tk.Button(self.button_frame, text="Start", command=self.start_timer, bg="#4CAF50", fg="white", activebackground="#45a049")
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.pause_button = tk.Button(self.button_frame, text="Pause", command=self.pause_timer, bg="#f44336", fg="white", activebackground="#d32f2f")
        self.pause_button.pack(side=tk.LEFT, padx=5)

        self.reset_button = tk.Button(self.button_frame, text="Reset", command=self.reset_timer, bg="#008CBA", fg="white", activebackground="#007bb5")
        self.reset_button.pack(side=tk.LEFT, padx=5)

        self.end_session_button = tk.Button(self.button_frame, text="End", command=self.end_session, bg="#FF9800", fg="white", activebackground="#F57C00")
        self.end_session_button.pack(side=tk.LEFT, padx=5)

        self.extended_break_button = tk.Button(self.button_frame, text="Extended Break", command=self.extended_break, bg="#FF5722", fg="white", activebackground="#E64A19")
        self.extended_break_button.pack(side=tk.LEFT, padx=5)

        # Task management
        self.task_frame = tk.Frame(root)
        self.task_frame.pack(pady=10)

        self.task_entry = tk.Entry(self.task_frame, width=40, bg="#333", fg="white", insertbackground="white")
        self.task_entry.pack(side=tk.LEFT, padx=5)

        self.add_task_button = tk.Button(self.task_frame, text="Add Task", command=self.add_task, bg="#555", fg="white", activebackground="#444")
        self.add_task_button.pack(side=tk.LEFT, padx=5)

        self.task_listbox = tk.Listbox(root, width=50, height=12, bg="#333", fg="white", selectbackground="#555", selectforeground="white")
        self.task_listbox.pack(pady=10)

        self.task_var = tk.IntVar()
        self.task_checkbox = tk.Checkbutton(root, text="Mark as Completed", variable=self.task_var, command=self.mark_task_completed, bg="#2c2c2c", fg="white", selectcolor="#555")
        self.task_checkbox.pack(pady=5)

        # Ensure the reset button is visible
        self.reset_button.pack(pady=5)

    def play_sound(self):
        playsound('notification.wav')

    def __init__(self, root):
        self.root = root
        self.root.title("Pomodoro Timer")
        self.root.attributes('-topmost', True)
        self.root.configure(bg="#2c2c2c")
        self.position_window()
        self.root.geometry(f"{self.window_width}x{self.window_height}")

        # Initialize database connection
        self.conn = create_connection()
        create_tables(self.conn)

        # Initialize progress bar value
        self.progress_bar_value = 0

    def update_progress_bar(self):
        if self.current_time == self.work_time:
            total_time = self.work_time
        else:
            total_time = self.break_time

        remaining_time = total_time - self.current_time
        self.progress_bar_value = (remaining_time / total_time) * 100
        self.progress_bar["value"] = self.progress_bar_value

    def format_time(self, seconds):
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02}:{seconds:02}"

    def start_timer(self):
        if not self.timer_running:
            self.timer_running = True
            self.start_time = time.strftime("%Y-%m-%d %H:%M:%S")
            self.session_id = insert_session(self.conn, self.start_time, None, "Work")
            self.run_timer()

    def pause_timer(self):
        if self.timer_running:
            self.timer_running = False
            self.pause_button.config(text="Resume")
        else:
            self.timer_running = True
            self.pause_button.config(text="Pause")
            self.run_timer()

    def end_session(self):
        if hasattr(self, 'session_id'):
            end_time = time.strftime("%Y-%m-%d %H:%M:%S")
            session_type = "Work" if self.current_time == self.work_time else "Break"
            insert_session(self.conn, self.start_time, end_time, session_type)
            self.start_time = None
            self.session_id = None
            self.timer_running = False
            if self.current_time == self.work_time:
                self.current_time = self.break_time
                self.time_label.config(text=self.format_time(self.current_time))
                self.start_timer()
            else:
                self.current_time = self.work_time
                self.time_label.config(text=self.format_time(self.current_time))
            self.task_entry.delete(0, tk.END)
            self.task_listbox.delete(0, tk.END)
            self.pause_button.config(text="Pause")
            self.play_sound()

    def run_timer(self):
        if self.timer_running and self.current_time > 0:
            self.current_time -= 1
            self.time_label.config(text=self.format_time(self.current_time))
            self.update_progress_bar()
            self.root.after(1000, self.run_timer)
        elif self.timer_running and self.current_time == 0:
            self.current_time = self.break_time
            self.time_label.config(text=self.format_time(self.current_time))
            self.play_sound()
            self.run_timer()
        elif not self.timer_running:
            pass

    def add_task(self):
        task = self.task_entry.get()
        if task and hasattr(self, 'session_id'):
            self.task_listbox.insert(tk.END, f"[ ] {task}")
            self.task_entry.delete(0, tk.END)
            insert_task(self.conn, self.session_id, task)

    def mark_task_completed(self):
        try:
            selected_index = self.task_listbox.curselection()[0]
            task_with_checkbox = self.task_listbox.get(selected_index)
            task = task_with_checkbox[4:]  # Remove the checkbox part
            completed = task_with_checkbox.startswith("[✓]")
            new_task_with_checkbox = "[✓] " + task if not completed else "[ ] " + task
            self.task_listbox.delete(selected_index)
            self.task_listbox.insert(selected_index, new_task_with_checkbox)
            if hasattr(self, 'session_id'):
                insert_task(self.conn, self.session_id, task, completed=not completed)
        except IndexError:
            pass

    def reset_timer(self):
        self.timer_running = False
        self.current_time = self.work_time
        self.time_label.config(text=self.format_time(self.current_time))
        self.progress_bar["value"] = 0
        self.task_entry.delete(0, tk.END)
        self.task_listbox.delete(0, tk.END)
        self.start_time = None
        self.session_id = None
        self.pause_button.config(text="Pause")

    def extended_break(self):
        if self.current_time != self.break_time:
            self.timer_running = False
            self.current_time = 15 * 60  # 15 minutes
            self.time_label.config(text=self.format_time(self.current_time))
            self.progress_bar["value"] = 0
            self.task_entry.delete(0, tk.END)
            self.task_listbox.delete(0, tk.END)
            self.start_time = None
            self.session_id = None
            self.pause_button.config(text="Pause")
            self.start_timer()

if __name__ == "__main__":
    root = tk.Tk()
    app = PomodoroTimer(root)
    root.mainloop()
