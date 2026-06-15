@echo off
cd /d "%~dp0"
echo BatchMonitor (Python)
python batch_monitor.py --once
echo Exit: %ERRORLEVEL%
pause
