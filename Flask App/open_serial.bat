@echo off
:loop
curl http://127.0.0.1:5000/all
timeout /t 15 >nul
goto loop