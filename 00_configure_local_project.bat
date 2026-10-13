@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo ERROR: Virtual environment not found. Run 01_install_windows.bat first.
    pause
    exit /b 1
)
".venv\Scripts\python.exe" "configure_local_project.py"
if errorlevel 1 (
    echo.
    echo Configuration NOT completed. Read the error message above.
    pause
    exit /b 1
)
echo.
echo Ready. Run 02_start_jupyter.bat next.
pause
