@echo off
REM Batch Monitor Launcher (.NET)
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"
echo [%date% %time%] Monitor started >> monitor_output.log
dotnet run --project . -- --once >> monitor_output.log 2>&1
echo [%date% %time%] Exit: %ERRORLEVEL% >> monitor_output.log
