@echo off
chcp 65001 > nul
cd /d "%~dp0"

echo ============================================
echo  Sample Data Generator
echo  Generating 100 sample responses...
echo ============================================
echo.

call venv\Scripts\activate
python scripts\generate_sample_data.py

echo.
echo ============================================
echo  Generation Complete!
echo ============================================
pause
