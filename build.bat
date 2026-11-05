@echo off
chcp 65001 >nul
title Samalyotcha EXE Builder

echo.
echo ==========================================
echo  SAMALYOTCHA - EXE YARATISH
echo ==========================================
echo.

:: Python borligini tekshirish
python --version >nul 2>&1
if errorlevel 1 (
    echo [XATO] Python topilmadi!
    echo  Python yuklab oling: https://python.org
    pause & exit /b 1
)

:: pip bor-yo'qligini tekshirish
pip --version >nul 2>&1
if errorlevel 1 (
    echo [XATO] pip topilmadi!
    pause & exit /b 1
)

echo [1/3] Kutubxonalar o'rnatilmoqda...
pip install pygame>=2.0.0 pyinstaller>=6.0.0 --quiet
if errorlevel 1 (
    echo [XATO] O'rnatish muvaffaqiyatsiz!
    pause & exit /b 1
)

echo [2/3] EXE yaratilmoqda...
python build.py
if errorlevel 1 (
    echo [XATO] Build muvaffaqiyatsiz!
    pause & exit /b 1
)

echo.
echo ==========================================
echo  TAYYOR! dist\Samalyotcha\Samalyotcha.exe
echo ==========================================
echo.
pause
