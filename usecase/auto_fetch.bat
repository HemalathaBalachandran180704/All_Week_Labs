@echo off
start "" cmd /c "python app.py"
timeout /t 3 >nul

:loop
curl http://127.0.0.1:5000/next
echo.
timeout /t 5 >nul
goto loop
