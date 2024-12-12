# Pomodoro Desktop Timer

Tutorial: https://youtu.be/PRhXOYlrTzA

A simple yet powerful Pomodoro timer application built using Python and Tkinter.  This desktop app helps you manage your time effectively using the Pomodoro Technique, allowing you to track work sessions, breaks, and tasks.

## Features

* **Customizable Work and Break Times:** Set your preferred work and break durations (in minutes) directly within the application.
* **Progress Bar:** Visually track the progress of your current work or break session.
* **Audio Notifications:** Receive audio alerts (requires `playsound` library and a `notification.wav` sound file in the same directory) at the end of each session.
* **Task Management:** Add, track, and mark tasks as completed within each Pomodoro session.  Completed tasks are persisted in a database.
* **Session Tracking:**  The application stores session data (start time, end time, type - work or break) in an SQLite database (`pomodoro_sessions.db`).
* **Extended Break Option:**  Take a longer break when needed.
* **Intuitive Interface:**  User-friendly interface designed for ease of use.
* **Persistent Task and Session Data:** Data is stored using SQLite, ensuring data persistence across application sessions.

## Installation

1. **Dependencies:** Make sure you have Python 3 installed.  Install the required libraries using pip:
   
   ```bash
   pip install -r requirements.txt
   ```
2. Run the Application: Execute the pomodoro_timer.py script:
  ```bash
  python pomodoro_timer.py
```
#### Enjoy! 


Database

The application uses an SQLite database (pomodoro_sessions.db) to store session and task data. The database schema is as follows:
    sessions table:
        id (INTEGER, PRIMARY KEY, AUTOINCREMENT): Unique identifier for each session.
        start_time (TEXT): Start time of the session.
        end_time (TEXT): End time of the session.
        type (TEXT): Type of session ("Work" or "Break").
    tasks table:
        id (INTEGER, PRIMARY KEY, AUTOINCREMENT): Unique identifier for each task.
        session_id (INTEGER, FOREIGN KEY referencing sessions.id): ID of the session the task belongs to.
        task (TEXT): Description of the task.
        completed (BOOLEAN): Indicates if the task is completed.


## Inspiration
Since this has started, we have been inspired by other Pomodoro desktop apps like:
- Post: https://www.reddit.com/r/pomodoro/comments/zal8xm/pomodoro_desktop_app/
-- Images: https://preview.redd.it/pomodoro-desktop-app-v0-8zsn1f2tdh3a1.png?width=1223&format=png&auto=webp&s=ac2c3620e684a64de6cfc715de6311345d56b992

Make any contributions you want!
