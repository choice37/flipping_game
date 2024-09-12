@echo off
set PORT=12345
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :%PORT%') do (
    echo PID: %%a
    taskkill /PID %%a /F
)
pause
