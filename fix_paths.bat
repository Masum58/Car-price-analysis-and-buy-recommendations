@echo off
echo ========================================
echo 🔧 Fixing File Paths...
echo ========================================
echo.

echo Fixing scrapers...
powershell -Command "(Get-Content scrapers\scrape_cars.py) -replace \"'cars_data\.json'\", \"'../data/raw/cars_data.json'\" | Set-Content scrapers\scrape_cars.py"

echo Fixing scripts...
powershell -Command "(Get-Content scripts\clean_real_data_only.py) -replace \"'cars_data\.json'\", \"'../data/raw/cars_data.json'\" | Set-Content scripts\clean_real_data_only.py"
powershell -Command "(Get-Content scripts\clean_real_data_only.py) -replace \"'cars_data_real_api_ready\.json'\", \"'../data/raw/cars_data_real_api_ready.json'\" | Set-Content scripts\clean_real_data_only.py"

echo Fixing app...
powershell -Command "(Get-Content app\ai_calculations.py) -replace \"'cars_data_real_api_ready\.json'\", \"'../data/raw/cars_data_real_api_ready.json'\" | Set-Content app\ai_calculations.py"

echo.
echo ✅ Paths updated!
echo.
pause