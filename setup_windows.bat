@echo off
echo ========================================================
echo    Daybook Automation - Windows Setup Assistant
echo ========================================================
echo.

REM 1. Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in your PATH.
    echo Please download and install Python from https://www.python.org/
    echo IMPORTANT: Make sure to check "Add Python to PATH" during installation!
    pause
    exit /b 1
)

echo [1/3] Installing Python dependencies...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install requirements. Please check your internet connection.
    pause
    exit /b 1
)

echo.
echo [2/3] Installing Playwright Chromium browser...
python -m playwright install chromium
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install Playwright browser.
    pause
    exit /b 1
)

echo.
echo [3/3] Setting up configuration file (.env)...
if not exist ".env" (
    copy ".env.example" ".env"
    echo Created .env file from .env.example.
    echo Please open .env and put your own login email and password!
) else (
    echo .env file already exists.
)

echo.
echo ========================================================
echo    Setup Completed Successfully!
echo ========================================================
echo.
echo Next steps:
echo 1. Open the file named ".env" in Notepad and fill in your portal credentials.
echo 2. Run any of the following batch scripts by double-clicking:
echo    - run_vtu_courses.bat       : Complete 100%% VTU Online course videos
echo    - run_edutainer_courses.bat : Complete 100%% EduTrainer course videos
echo    - run_daily_diary.bat       : Submit today's VTU Internship Diary entry
echo.
pause
