import tkinter as tk
from tkinter import messagebox
import time

class PomodoroTimer:
    def __init__(self, root):
        self.root = root
        self.root.title("Pomodoro Timer")
        self.root.geometry("300x200")

        self.work_time = 25 * 60  # 25 minutes
        self.break_time = 5 * 60  # 5 minutes
        self.timer_running = False
        self.current_time = self.work_time

        self.time_label = tk.Label(root, text=self.format_time(self.current_time), font=("Helvetica", 48))
        self.time_label.pack(pady=20)

        self.start_button = tk.Button(root, text="Start", command=self.start_timer)
        self.start_button.pack(pady=5)

        self.stop_button = tk.Button(root, text="Stop", command=self.stop_timer)
        self.stop_button.pack(pady=5)

        self.reset_button = tk.Button(root, text="Reset", command=self.reset_timer)
        self.reset_button.pack(pady=5)

    def format_time(self, seconds):
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02}:{seconds:02}"

    def start_timer(self):
        if not self.timer_running:
            self.timer_running = True
            self.run_timer()

    def stop_timer(self):
        self.timer_running = False

    def reset_timer(self):
        self.timer_running = False
        self.current_time = self.work_time
        self.time_label.config(text=self.format_time(self.current_time))

    def run_timer(self):
        if self.timer_running and self.current_time > 0:
            self.current_time -= 1
            self.time_label.config(text=self.format_time(self.current_time))
            self.root.after(1000, self.run_timer)
        elif self.timer_running and self.current_time == 0:
            messagebox.showinfo("Time's up!", "Break time!")
            self.current_time = self.break_time
            self.time_label.config(text=self.format_time(self.current_time))
            self.run_timer()

if __name__ == "__main__":
    root = tk.Tk()
    app = PomodoroTimer(root)
    root.mainloop()
