@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo ERROR: .venv not found. Run 01_install_windows.bat first.
  pause
  exit /b 1
)
".venv\Scripts\python.exe" -m pip install -r "requirements_portfolio.txt"
if errorlevel 1 (
  echo ERROR: Dependency installation failed.
  pause
  exit /b 1
)
echo Portfolio packages installed successfully.
pause
