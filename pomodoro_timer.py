import tkinter as tk
from tkinter import messagebox, ttk
import time
import sqlite3
from database import create_connection, create_tables, insert_session, insert_task
import os
import math
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

class PomodoroTimer:
    def __init__(self, root):
        self.root = root
        self.root.title("Pomodoro")
        self.style = ttk.Style(theme="darkly")
        
        # Configure icon font
        self.style.configure("Custom.TButton", font=("Font Awesome 6 Free Solid", 12))
        
        # Font Awesome icon unicode characters
        self.ICON_PLAY = "\uf04b"
        self.ICON_PAUSE = "\uf04c"
        self.ICON_RESET = "\uf01e"
        self.ICON_SETTINGS = "\uf013"
        self.ICON_TASKS = "\uf0ae"
        self.ICON_ADD = "\uf067"
        self.ICON_REMOVE = "\uf00d"
        self.ICON_BREAK = "\uf0f4"
        self.ICON_CHECK = "\uf00c"
        self.ICON_EXPAND = "\uf077"
        self.ICON_COLLAPSE = "\uf078"
        
        self.position_window()
        self.root.geometry(f"{self.window_width}x{self.window_height}")

        # Initialize database connection
        self.conn = create_connection()
        create_tables(self.conn)

        # Initialize progress bar value
        self.progress_bar_value = 0

        # Initialize timer variables
        self.default_work_time = 25 * 60
        self.default_break_time = 5 * 60
        self.extended_break_time = 15 * 60
        self.work_time = self.default_work_time
        self.break_time = self.default_break_time
        self.timer_running = False
        self.current_time = self.work_time
        self.tasks_expanded = False

        # Create main container with dark theme
        self.main_container = ttk.Frame(self.root, style="Custom.TFrame")
        self.main_container.pack(expand=True, fill="both", padx=5, pady=5)

        # Top toolbar
        self.toolbar = ttk.Frame(self.main_container)
        self.toolbar.pack(fill="x", pady=(0, 5))

        # Settings button
        self.settings_btn = ttk.Button(
            self.toolbar,
            text=self.ICON_SETTINGS,
            style="Custom.TButton",
            command=self.toggle_settings,
            width=3
        )
        self.create_tooltip(self.settings_btn, "Settings")
        self.settings_btn.pack(side=tk.RIGHT, padx=2)

        # Tasks button
        self.tasks_btn = ttk.Button(
            self.toolbar,
            text=self.ICON_TASKS,
            style="Custom.TButton",
            command=self.toggle_tasks,
            width=3
        )
        self.create_tooltip(self.tasks_btn, "Tasks")
        self.tasks_btn.pack(side=tk.RIGHT, padx=2)

        # Settings frame (initially hidden)
        self.settings_frame = ttk.Frame(self.main_container)
        
        ttk.Label(
            self.settings_frame,
            text="Work:"
        ).pack(side=tk.LEFT, padx=2)
        
        self.work_spinbox = ttk.Spinbox(
            self.settings_frame,
            from_=1,
            to=60,
            width=2,
            increment=1
        )
        self.work_spinbox.delete(0, tk.END)
        self.work_spinbox.insert(0, "25")
        self.work_spinbox.pack(side=tk.LEFT, padx=2)

        ttk.Label(
            self.settings_frame,
            text="Break:"
        ).pack(side=tk.LEFT, padx=2)
        
        self.break_spinbox = ttk.Spinbox(
            self.settings_frame,
            from_=1,
            to=30,
            width=2,
            increment=1
        )
        self.break_spinbox.delete(0, tk.END)
        self.break_spinbox.insert(0, "5")
        self.break_spinbox.pack(side=tk.LEFT, padx=2)

        # Apply button
        self.apply_settings = ttk.Button(
            self.settings_frame,
            text=self.ICON_CHECK,
            style="Custom.TButton",
            command=self.apply_time_settings,
            width=3
        )
        self.create_tooltip(self.apply_settings, "Apply Settings")
        self.apply_settings.pack(side=tk.LEFT, padx=2)

        # Timer display
        self.time_label = ttk.Label(
            self.main_container,
            text=self.format_time(self.current_time),
            font=("Helvetica", 36),
            style="Custom.TLabel"
        )
        self.time_label.pack(pady=5)

        # Progress bar
        self.progress_bar = ttk.Progressbar(
            self.main_container,
            length=200,
            mode="determinate",
            style="Custom.Horizontal.TProgressbar"
        )
        self.progress_bar.pack(pady=5)

        # Control buttons frame
        self.button_frame = ttk.Frame(self.main_container)
        self.button_frame.pack(pady=5)

        # Start/Pause button
        self.start_pause_button = ttk.Button(
            self.button_frame,
            text=self.ICON_PLAY,
            style="Custom.TButton",
            command=self.toggle_timer,
            width=3
        )
        self.create_tooltip(self.start_pause_button, "Start/Pause Timer")
        self.start_pause_button.pack(side=tk.LEFT, padx=5)

        # Reset button
        self.reset_button = ttk.Button(
            self.button_frame,
            text=self.ICON_RESET,
            style="Custom.TButton",
            command=self.reset_timer,
            width=3
        )
        self.create_tooltip(self.reset_button, "Reset Timer")
        self.reset_button.pack(side=tk.LEFT, padx=5)

        # Tasks frame (initially hidden)
        self.tasks_frame = ttk.Frame(self.main_container)
        
        # Task entry frame
        self.task_entry_frame = ttk.Frame(self.tasks_frame)
        self.task_entry_frame.pack(fill="x", padx=5, pady=2)
        
        self.task_entry = ttk.Entry(
            self.task_entry_frame
        )
        self.task_entry.pack(side=tk.LEFT, expand=True, fill="x", padx=(0, 5))
        
        self.add_task_btn = ttk.Button(
            self.task_entry_frame,
            text=self.ICON_ADD,
            style="Custom.TButton",
            command=self.add_task,
            width=3
        )
        self.create_tooltip(self.add_task_btn, "Add Task")
        self.add_task_btn.pack(side=tk.LEFT)

        # Task list
        self.task_listbox = tk.Listbox(
            self.tasks_frame,
            height=5,
            selectmode=tk.SINGLE,
            bg=self.style.colors.dark,
            fg=self.style.colors.light,
            selectbackground=self.style.colors.primary
        )
        self.task_listbox.pack(fill="both", expand=True, padx=5, pady=2)
        
        # Task controls frame
        self.task_controls = ttk.Frame(self.tasks_frame)
        self.task_controls.pack(fill="x", padx=5, pady=2)
        
        self.remove_task_btn = ttk.Button(
            self.task_controls,
            text=self.ICON_REMOVE,
            style="Custom.TButton",
            command=self.remove_task,
            width=3
        )
        self.create_tooltip(self.remove_task_btn, "Remove Task")
        self.remove_task_btn.pack(side=tk.LEFT)
        
        self.extended_break_btn = ttk.Button(
            self.task_controls,
            text=self.ICON_BREAK,
            style="Custom.TButton",
            command=self.extended_break,
            width=3
        )
        self.create_tooltip(self.extended_break_btn, "Take Extended Break")
        self.extended_break_btn.pack(side=tk.RIGHT)

    def create_tooltip(self, widget, text):
        """Create a tooltip for a widget"""
        def enter(event):
            self.tooltip = tk.Toplevel()
            self.tooltip.wm_overrideredirect(True)
            self.tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            
            label = ttk.Label(
                self.tooltip,
                text=text,
                style="Custom.TLabel",
                padding=(5, 2)
            )
            label.pack()

        def leave(event):
            if hasattr(self, "tooltip"):
                self.tooltip.destroy()
                del self.tooltip

        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)

    def toggle_tasks(self):
        """Toggle tasks panel visibility"""
        if self.tasks_frame.winfo_ismapped():
            self.tasks_frame.pack_forget()
            self.window_height = 200
            self.tasks_expanded = False
            self.tasks_btn.configure(text=self.ICON_EXPAND)
        else:
            self.tasks_frame.pack(fill="both", expand=True, pady=5)
            self.window_height = 350
            self.tasks_expanded = True
            self.tasks_btn.configure(text=self.ICON_COLLAPSE)
        
        # Update window size
        self.root.geometry(f"{self.window_width}x{self.window_height}")

    def toggle_timer(self):
        if self.timer_running:
            self.timer_running = False
            self.start_pause_button.configure(text=self.ICON_PLAY)
        else:
            self.timer_running = True
            self.start_pause_button.configure(text=self.ICON_PAUSE)
            self.update_timer()

    def position_window(self):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.window_width = 250  # Even more compact width
        self.window_height = 200  # Even more compact height
        x = screen_width - self.window_width - 20
        y = screen_height - self.window_height - 50
        self.root.geometry(f"{self.window_width}x{self.window_height}+{x}+{y}")

    def toggle_settings(self):
        """Toggle visibility of time settings"""
        if self.settings_frame.winfo_ismapped():
            self.settings_frame.pack_forget()
        else:
            self.settings_frame.pack(pady=5, before=self.time_label)

    def create_notification_sound(self):
        """Create a simple notification sound using winsound"""
        import winsound
        import wave
        import struct
        
        # Create a simple "ding" sound
        duration = 0.1  # seconds
        frequency = 440  # Hz (A4 note)
        sample_rate = 44100
        amplitude = 32767
        num_samples = int(duration * sample_rate)
        
        # Generate samples
        samples = []
        for i in range(num_samples):
            t = float(i) / sample_rate
            sample = amplitude * math.sin(2 * math.pi * frequency * t)
            samples.append(int(sample))
        
        # Write WAV file
        with wave.open(self.sound_file, 'w') as wav_file:
            # Set parameters
            nchannels = 1
            sampwidth = 2
            framerate = sample_rate
            nframes = num_samples
            comptype = 'NONE'
            compname = 'not compressed'
            
            # Set WAV file parameters
            wav_file.setparams((nchannels, sampwidth, framerate, nframes, comptype, compname))
            
            # Write the samples
            for sample in samples:
                wav_file.writeframes(struct.pack('h', sample))

    def play_sound(self):
        """Play notification sound"""
        try:
            import winsound
            winsound.PlaySound(self.sound_file, winsound.SND_FILENAME)
        except Exception as e:
            print(f"Could not play sound: {e}")

    def format_time(self, seconds):
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02}:{seconds:02}"

    def end_session(self):
        if self.timer_running:
            self.timer_running = False
            self.current_time = (
                0  # This will trigger the transition to the next segment
            )
            self.time_label.config(text=self.format_time(self.current_time))
            self.progress_bar["value"] = 100
            self.start_pause_button.config(
                text="Start", bg="#4CAF50", activebackground="#45a049"
            )
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
            if hasattr(self, "session_id"):
                end_time = time.strftime("%Y-%m-%d %H:%M:%S")
                session_type = (
                    "Work" if self.current_time == self.work_time else "Break"
                )
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
            self.start_pause_button.config(
                text="Start", bg="#4CAF50", activebackground="#45a049"
            )

    def add_task(self):
        task = self.task_entry.get().strip()
        if task:
            self.task_listbox.insert(tk.END, task)
            self.task_entry.delete(0, tk.END)
            # Only insert task if there's an active session
            if hasattr(self, 'session_id') and self.session_id is not None:
                insert_task(self.conn, self.session_id, task)

    def remove_task(self):
        selection = self.task_listbox.curselection()
        if selection:
            self.task_listbox.delete(selection)

    def extended_break(self):
        if not self.timer_running:
            self.current_time = self.extended_break_time
            self.time_label.config(text=self.format_time(self.current_time))
            self.progress_bar["value"] = 0

    def reset_timer(self):
        self.timer_running = False
        self.current_time = self.work_time
        self.time_label.config(text=self.format_time(self.current_time))
        self.progress_bar["value"] = 0
        self.task_entry.delete(0, tk.END)
        self.task_listbox.delete(0, tk.END)
        self.start_time = None
        self.session_id = None
        self.start_pause_button.config(
            text=self.ICON_PLAY
        )

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
                messagebox.showwarning(
                    "Warning", "Cannot change time settings while timer is running!"
                )
        except ValueError:
            messagebox.showerror(
                "Error", "Please enter valid numbers for work and break times"
            )

    def update_progress_bar(self):
        if self.current_time == self.work_time:
            total_time = self.work_time
        else:
            total_time = self.break_time

        remaining_time = total_time - self.current_time
        self.progress_bar_value = (remaining_time / total_time) * 100
        self.progress_bar["value"] = self.progress_bar_value

    def update_timer(self):
        if not self.timer_running:
            return

        if self.current_time > 0:
            self.current_time -= 1
            self.time_label.config(text=self.format_time(self.current_time))
            self.update_progress_bar()
            self.root.after(1000, self.update_timer)
        elif self.current_time == 0:
            self.timer_running = False
            self.play_sound()

            # Switch between work and break time
            if hasattr(self, "session_id"):
                end_time = time.strftime("%Y-%m-%d %H:%M:%S")
                session_type = (
                    "Work" if self.current_time == self.work_time else "Break"
                )
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
            self.start_pause_button.config(
                text="Start", bg="#4CAF50", activebackground="#45a049"
            )

if __name__ == "__main__":
    root = tk.Tk()
    app = PomodoroTimer(root)
    root.mainloop()
