@echo off
@REM pip install -r requirements.txt
@REM pip install pyinstaller
pyinstaller --onefile --windowed pomodoro_timer.py
echo Executable created in dist\pomodoro_timer.exe
