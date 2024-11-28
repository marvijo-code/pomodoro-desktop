@echo off
pip install -r requirements.txt
pyinstaller --onefile --windowed pomodoro_timer.py
echo Executable created in dist\pomodoro_timer.exe
