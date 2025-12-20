@echo off
setlocal enabledelayedexpansion

echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║                                                          ║
echo ║     🏗️  Professional Project Restructure Tool          ║
echo ║                                                          ║
echo ╚══════════════════════════════════════════════════════════╝
echo.

echo ⚠️  This will reorganize your project structure.
echo    A backup will be created first.
echo.
set /p confirm="Continue? (y/n): "
if /i not "%confirm%"=="y" (
    echo.
    echo ❌ Cancelled.
    exit /b
)

echo.
echo ========================================
echo 📦 Creating Backup...
echo ========================================

set backup_folder=backup_%date:~-4,4%%date:~-7,2%%date:~-10,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set backup_folder=%backup_folder: =0%
mkdir "%backup_folder%" 2>nul
xcopy *.* "%backup_folder%\" /Y /Q >nul 2>&1

echo ✅ Backup created: %backup_folder%
echo.

echo ========================================
echo 🏗️  Creating Folder Structure...
echo ========================================

REM Create folders
for %%d in (app app\api app\models app\services app\utils scrapers data data\raw data\processed data\backup data\ml_models scripts tests docs logs config) do (
    mkdir "%%d" 2>nul
    echo ✅ %%d
)

echo.
echo ========================================
echo 📦 Moving Files...
echo ========================================

REM Move data files
echo Moving data files...
for %%f in (cars_data*.json cars_data*.csv) do (
    if exist "%%f" (
        move "%%f" "data\raw\" >nul 2>&1
        echo ✅ %%f → data\raw\
    )
)

REM Move ML models
echo Moving ML models...
for %%f in (ml_model*.joblib ml_model*.json) do (
    if exist "%%f" (
        move "%%f" "data\ml_models\" >nul 2>&1
        echo ✅ %%f → data\ml_models\
    )
)

REM Move scrapers
echo Moving scrapers...
for %%f in (scrape*.py autoscout*.py) do (
    if exist "%%f" (
        move "%%f" "scrapers\" >nul 2>&1
        echo ✅ %%f → scrapers\
    )
)

REM Move scripts
echo Moving scripts...
for %%f in (clean_*.py check_*.py show_*.py verify_*.py track_*.py analyze_*.py manual_*.py generate_*.py update_*.py test_*.py train_*.py demo_*.py fix_*.py integrate_*.py weekly_*.py) do (
    if exist "%%f" (
        move "%%f" "scripts\" >nul 2>&1
        echo ✅ %%f → scripts\
    )
)

echo.
echo ========================================
echo 📝 Creating Documentation...
echo ========================================

REM Create .gitignore
echo # Environment> .gitignore
echo .env>> .gitignore
echo venv/>> .gitignore
echo __pycache__/>> .gitignore
echo *.pyc>> .gitignore
echo.>> .gitignore
echo # Data>> .gitignore
echo data/raw/*.json>> .gitignore
echo data/raw/*.csv>> .gitignore
echo data/backup/>> .gitignore
echo *.log>> .gitignore
echo.>> .gitignore
echo # Models>> .gitignore
echo data/ml_models/*.joblib>> .gitignore
echo.>> .gitignore
echo # IDE>> .gitignore
echo .vscode/>> .gitignore
echo .idea/>> .gitignore
echo *.swp>> .gitignore
echo ✅ .gitignore

REM Create README.md
echo # Car Price Analysis ^& Buy Recommendations> docs\README.md
echo.>> docs\README.md
echo AI-powered car market analysis for Belgian marketplaces.>> docs\README.md
echo.>> docs\README.md
echo ## Quick Start>> docs\README.md
echo.>> docs\README.md
echo ```bash>> docs\README.md
echo # Scrape data>> docs\README.md
echo python scrapers\scrape_cars.py>> docs\README.md
echo.>> docs\README.md
echo # Clean data>> docs\README.md
echo python scripts\clean_data.py>> docs\README.md
echo.>> docs\README.md
echo # Start API>> docs\README.md
echo uvicorn app.main:app --reload>> docs\README.md
echo ```>> docs\README.md
echo ✅ docs\README.md

echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║                                                          ║
echo ║              ✅ Restructure Complete!                   ║
echo ║                                                          ║
echo ╚══════════════════════════════════════════════════════════╝
echo.

echo 📊 New Structure:
tree /F /A | more

echo.
echo 📋 Next Steps:
echo    1. Review moved files
echo    2. Update import paths in code
echo    3. Test application
echo    4. Commit to git
echo.
echo 💾 Backup location: %backup_folder%
echo.

pause