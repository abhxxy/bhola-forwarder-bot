@echo off
title Bhola Updates Telegram Forwarder
echo ===================================================
echo     Starting Bhola Updates Telegram Forwarder
echo ===================================================
echo.
python -m pip install -r requirements.txt
python main.py
pause
