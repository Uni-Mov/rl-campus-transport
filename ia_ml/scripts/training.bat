@echo off

cd /d "%~dp0\.."
python -m src.training.main

echo.
pause