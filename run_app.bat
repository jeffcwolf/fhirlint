@echo off
REM FHIR Quality Inspector Launcher for Windows

cd /d %~dp0

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Run application
python src\main.py
