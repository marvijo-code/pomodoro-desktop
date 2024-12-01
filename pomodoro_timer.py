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
        self.window_height = 350
        x = screen_width - self.window_width
        y = screen_height - self.window_height - 50  # Adjust y position to start a bit higher
        self.root.geometry(f"{self.window_width}x{self.window_height}+{x}+{y}")

        # Initialize timer variables
        self.default_work_time = 25 * 60  # 25 minutes
        self.default_break_time = 5 * 60  # 5 minutes
        self.work_time = self.default_work_time
        self.break_time = self.default_break_time
        self.timer_running = False
        self.current_time = self.work_time

        # Time settings frame
        self.settings_frame = tk.Frame(self.root, bg="#2c2c2c")
        self.settings_frame.pack(pady=5)
        
        # Work time settings
        tk.Label(self.settings_frame, text="Work (min):", bg="#2c2c2c", fg="white").pack(side=tk.LEFT, padx=2)
        self.work_spinbox = tk.Spinbox(self.settings_frame, from_=1, to=60, width=3, bg="#333", fg="white")
        self.work_spinbox.delete(0, tk.END)
        self.work_spinbox.insert(0, "25")
        self.work_spinbox.pack(side=tk.LEFT, padx=2)
        
        # Break time settings
        tk.Label(self.settings_frame, text="Break (min):", bg="#2c2c2c", fg="white").pack(side=tk.LEFT, padx=2)
        self.break_spinbox = tk.Spinbox(self.settings_frame, from_=1, to=30, width=3, bg="#333", fg="white")
        self.break_spinbox.delete(0, tk.END)
        self.break_spinbox.insert(0, "5")
        self.break_spinbox.pack(side=tk.LEFT, padx=2)
        
        # Apply settings button
        self.apply_settings = tk.Button(self.settings_frame, text="Apply", command=self.apply_time_settings, 
                                      bg="#555", fg="white", activebackground="#444")
        self.apply_settings.pack(side=tk.LEFT, padx=5)

        self.time_label = tk.Label(self.root, text=self.format_time(self.current_time), font=("Helvetica", 48), bg="#2c2c2c", fg="white")
        self.time_label.pack(pady=10)

        self.progress_bar = ttk.Progressbar(self.root, orient="horizontal", length=300, mode="determinate")
        self.progress_bar.pack(pady=10)

        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(pady=5)

        self.start_pause_button = tk.Button(self.button_frame, text="Start", command=self.toggle_timer, 
                                          bg="#4CAF50", fg="white", activebackground="#45a049")
        self.start_pause_button.pack(side=tk.LEFT, padx=5)

        self.reset_button = tk.Button(self.button_frame, text="Reset", command=self.reset_timer, 
                                    bg="#008CBA", fg="white", activebackground="#007bb5")
        self.reset_button.pack(side=tk.LEFT, padx=5)

        self.end_session_button = tk.Button(self.button_frame, text="End", command=self.end_session, 
                                          bg="#FF9800", fg="white", activebackground="#F57C00")
        self.end_session_button.pack(side=tk.LEFT, padx=5)

        self.extended_break_button = tk.Button(self.button_frame, text="Extended Break", 
                                             command=self.extended_break, bg="#FF5722", 
                                             fg="white", activebackground="#E64A19", 
                                             state=tk.DISABLED if self.current_time == self.break_time else tk.NORMAL)
        self.extended_break_button.pack(side=tk.LEFT, padx=5)

        # Task management
        self.task_frame = tk.Frame(self.root)
        self.task_frame.pack(pady=5)

        self.task_entry = tk.Entry(self.task_frame, width=40, bg="#333", fg="white", insertbackground="white")
        self.task_entry.pack(side=tk.LEFT, padx=5)

        self.add_task_button = tk.Button(self.task_frame, text="Add Task", command=self.add_task, bg="#555", fg="white", activebackground="#444")
        self.add_task_button.pack(side=tk.LEFT, padx=5)

        # Task list frame
        self.task_list_frame = tk.Frame(self.root, bg="#2c2c2c")
        self.task_list_frame.pack(pady=5)

        self.task_listbox = tk.Listbox(self.task_list_frame, width=50, height=8, bg="#333", fg="white", selectbackground="#555", selectforeground="white")
        self.task_listbox.pack(side=tk.LEFT, pady=5)

        # Task buttons frame
        self.task_buttons_frame = tk.Frame(self.task_list_frame, bg="#2c2c2c")
        self.task_buttons_frame.pack(side=tk.LEFT, padx=5)

        self.remove_task_button = tk.Button(self.task_buttons_frame, text="Remove", command=self.remove_task,
                                          bg="#f44336", fg="white", activebackground="#d32f2f")
        self.remove_task_button.pack(pady=2)

        self.task_var = tk.IntVar()
        self.task_checkbox = tk.Checkbutton(self.root, text="Mark as Completed", variable=self.task_var, 
                                          command=self.mark_task_completed, bg="#2c2c2c", fg="white", selectcolor="#555")
        self.task_checkbox.pack(pady=5)

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

    def toggle_timer(self):
        if not self.timer_running:
            self.timer_running = True
            self.start_pause_button.config(text="Pause", bg="#f44336", activebackground="#d32f2f")
            if not hasattr(self, 'start_time'):
                self.start_time = time.strftime("%Y-%m-%d %H:%M:%S")
                self.session_id = insert_session(self.conn, self.start_time, None, "Work")
            self.run_timer()
        else:
            self.timer_running = False
            self.start_pause_button.config(text="Resume", bg="#4CAF50", activebackground="#45a049")

    def pause_timer(self):
        if self.timer_running:
            self.timer_running = False
            self.pause_button.config(text="Resume")
        else:
            self.timer_running = True
            self.pause_button.config(text="Pause")
            self.run_timer()

    def end_session(self):
        if self.timer_running:
            self.timer_running = False
            self.current_time = 0  # This will trigger the transition to the next segment
            self.time_label.config(text=self.format_time(self.current_time))
            self.progress_bar["value"] = 100
            self.start_pause_button.config(text="Start", bg="#4CAF50", activebackground="#45a049")
            self.play_sound()

    def run_timer(self):
        if not self.timer_running:
            return
            
        if self.current_time > 0:
            self.current_time -= 1
            self.time_label.config(text=self.format_time(self.current_time))
            self.update_progress_bar()
            self.root.after(1000, self.run_timer)
        elif self.current_time == 0:
            self.timer_running = False
            self.play_sound()
            
            # Switch between work and break time
            if hasattr(self, 'session_id'):
                end_time = time.strftime("%Y-%m-%d %H:%M:%S")
                session_type = "Work" if self.current_time == self.work_time else "Break"
                insert_session(self.conn, self.start_time, end_time, session_type)
                self.start_time = None
                self.session_id = None
            
            if self.current_time == self.work_time:
                self.current_time = self.break_time
                self.extended_break_button.config(state=tk.DISABLED)
            else:
                self.current_time = self.work_time
                self.extended_break_button.config(state=tk.NORMAL)
            
            self.time_label.config(text=self.format_time(self.current_time))
            self.progress_bar["value"] = 0
            self.start_pause_button.config(text="Start", bg="#4CAF50", activebackground="#45a049")

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
        self.start_pause_button.config(text="Start", bg="#4CAF50", activebackground="#45a049")

    def extended_break(self):
        self.timer_running = False
        self.current_time = 15 * 60  # 15 minutes
        self.time_label.config(text=self.format_time(self.current_time))
        self.progress_bar["value"] = 0
        self.task_entry.delete(0, tk.END)
        self.task_listbox.delete(0, tk.END)
        self.start_time = None
        self.session_id = None
        self.start_pause_button.config(text="Start", bg="#4CAF50", activebackground="#45a049")
        self.extended_break_button.config(state=tk.DISABLED)  # Disable extended break button
        self.run_timer()

    def remove_task(self):
        selection = self.task_listbox.curselection()
        if selection:
            self.task_listbox.delete(selection)

    def apply_time_settings(self):
        try:
            new_work_time = int(self.work_spinbox.get()) * 60
            new_break_time = int(self.break_spinbox.get()) * 60
            
            # Only update times if timer is not running
            if not self.timer_running:
                self.work_time = new_work_time
                self.break_time = new_break_time
                self.current_time = new_work_time  # Reset current time to new work time
                self.time_label.config(text=self.format_time(self.current_time))
                # Reset progress bar
                self.progress_bar["value"] = 0
            else:
                messagebox.showwarning("Warning", "Cannot change time settings while timer is running!")
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for work and break times")

if __name__ == "__main__":
    root = tk.Tk()
    app = PomodoroTimer(root)
    root.mainloop()
