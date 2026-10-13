@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\activate.bat" (echo Run 01_install_windows.bat first. & pause & exit /b 1)
call ".venv\Scripts\activate.bat"
python -m pytest -q tests
pause
