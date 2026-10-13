@echo off
setlocal
cd /d "%~dp0"
echo ================================================
echo Hakaluki Haor - installing Jupyter requirements
echo Working folder: %CD%
echo ================================================
if not exist "config\settings.json" (
 echo ERROR: config\settings.json not found. Extract the ZIP into F:\Wetland Test directly.
 pause & exit /b 1
)
rem Prefer a supported 64-bit Python 3.12 or 3.11 through the Python Launcher.
set "PY_CMD=python"
where py >nul 2>nul
if not errorlevel 1 (
  py -3.12 --version >nul 2>nul
  if not errorlevel 1 (
    set "PY_CMD=py -3.12"
  ) else (
    py -3.11 --version >nul 2>nul
    if not errorlevel 1 set "PY_CMD=py -3.11"
  )
)
%PY_CMD% -m venv ".venv"
if errorlevel 1 (echo ERROR creating Python venv. Install Python 3.11 or 3.12. & pause & exit /b 1)
call ".venv\Scripts\activate.bat"
python -m pip install --upgrade pip
if %errorlevel% neq 0 (echo ERROR upgrading pip. & pause & exit /b 1)
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (echo ERROR installing packages. & pause & exit /b 1)
python -m ipykernel install --user --name hakaluki-haor --display-name "Python (Hakaluki Haor)"
if %errorlevel% neq 0 (echo ERROR installing kernel. & pause & exit /b 1)
echo.
echo SUCCESS. Open 02_start_jupyter.bat
pause
