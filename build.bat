@echo off
chcp 65001 >nul 2>&1
title Samalyotcha EXE Builder
color 0A

echo.
echo  ============================================================
echo   SAMALYOTCHA  -  EXE YARATISH
echo  ============================================================
echo.

:: Python borligini tekshirish
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    color 0C
    echo  [XATO] Python topilmadi!
    echo.
    echo  Iltimos Python yuklab o'rnating:
    echo  https://www.python.org/downloads/
    echo.
    echo  O'rnatishda "Add Python to PATH" belgisini qo'ying!
    echo.
    pause
    exit /b 1
)

echo  [OK] Python topildi
python --version

echo.
echo  [1/3] Kutubxonalar tekshirilmoqda va o'rnatilmoqda...
echo.
pip install pygame>=2.0.0 --quiet --no-warn-script-location
if %ERRORLEVEL% NEQ 0 (
    color 0C
    echo  [XATO] pygame o'rnatilmadi!
    pause
    exit /b 1
)
echo  [OK] pygame tayyor

pip install pyinstaller>=6.0.0 --quiet --no-warn-script-location
if %ERRORLEVEL% NEQ 0 (
    color 0C
    echo  [XATO] pyinstaller o'rnatilmadi!
    pause
    exit /b 1
)
echo  [OK] pyinstaller tayyor

echo.
echo  [2/3] EXE yaratilmoqda... (2-5 daqiqa)
echo.

python build.py
if %ERRORLEVEL% NEQ 0 (
    color 0C
    echo.
    echo  [XATO] Build muvaffaqiyatsiz tugadi!
    echo.
    echo  Iltimos:
    echo  1. Antivirus o'chirib ko'ring
    echo  2. Build.bat ni administrator sifatida ishga tushiring
    echo  3. dist\ va _build_tmp\ papkalarini qo'lda o'chirib qayta urining
    echo.
    pause
    exit /b 1
)

echo.
color 0A
echo  ============================================================
echo   TAYYOR!
echo   dist\Samalyotcha\Samalyotcha.exe
echo.
echo   Bu papkani istalgan kompyuterga ko'chiring.
echo   Python yoki pygame kerak emas!
echo  ============================================================
echo.

:: EXE papkasini Explorer da ochish
if exist "dist\Samalyotcha\Samalyotcha.exe" (
    echo  Explorer da ochilmoqda...
    explorer "dist\Samalyotcha"
)

pause
