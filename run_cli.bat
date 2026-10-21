@echo off
chcp 65001 >nul
title Zoom Bot CLI Runner
color 0A
cls

if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

python main.py
pause
