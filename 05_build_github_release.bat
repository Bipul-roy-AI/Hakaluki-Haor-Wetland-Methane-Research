@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo ERROR: .venv not found. Run 01_install_windows.bat first.
  pause
  exit /b 1
)
".venv\Scripts\python.exe" "build_github_release.py"
if errorlevel 1 (
  echo Export failed. Check the error above.
  pause
  exit /b 1
)
echo.
echo GitHub portfolio export completed. Open results\github_release\index.html
pause
