@echo off
title Product-Expiry-Bot
cd /d "%~dp0"

echo ==============================================
echo     INSTANT BILL & EXPIRY DATE ALERT BOT
echo ==============================================
echo.

if not exist .env (
    if exist .env.example (
        copy .env.example .env
        echo Created .env template. Please configure your TELEGRAM_BOT_TOKEN and GEMINI_API_KEY!
    )
)

:: Create dedicated named executable so Task Manager displays 'expiry-bot.exe' instead of generic 'python.exe'
for /f "delims=" %%i in ('where python') do set PYTHON_BIN=%%i & goto :found_py
:found_py

if not exist expiry-bot.exe (
    copy "%PYTHON_BIN%" expiry-bot.exe >nul
)

echo Starting Product Expiry Bot as [expiry-bot.exe]...
expiry-bot.exe bot.py
pause
