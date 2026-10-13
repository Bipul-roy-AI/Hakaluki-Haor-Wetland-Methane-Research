
@echo off
setlocal

REM Set project directory
set "PROJECT_DIR=F:\Wetland Test\Hakaluki_Haor_Wetland_Test_Jupyter_GEE_Project"

REM Change to project directory
cd /d "%PROJECT_DIR%"

REM Check virtual environment
if not exist ".venv\Scripts\python.exe" (
    echo ERROR: Python virtual environment not found.
    pause
    exit /b 1
)

REM Launch JupyterLab from project directory
echo Starting JupyterLab...
echo Working directory: %CD%

".venv\Scripts\python.exe" -m jupyter lab --notebook-dir="%PROJECT_DIR%" --no-browser

pause
