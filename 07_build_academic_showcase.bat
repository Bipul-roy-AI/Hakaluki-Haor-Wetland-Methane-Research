@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo ERROR: The existing .venv was not found under %CD%
    pause
    exit /b 1
)
".venv\Scripts\python.exe" build_academic_showcase.py
if errorlevel 1 (
    echo Showcase builder failed. Review the error above.
) else (
    echo.
    echo Open docs\index.html to view the research gallery.
    echo Review README_ACADEMIC_PREVIEW.md before publication.
)
pause
