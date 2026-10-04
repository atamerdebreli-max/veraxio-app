@echo off
REM AI Uyumluluk Kutusu - Task Scheduler Kurulum
REM Bu script, gunluk otomatik calistirma icin gorev olusturur.
REM Yonetici olarak calistirilmalidir.

echo ============================================
echo AI Uyumluluk Kutusu - Task Scheduler Kurulum
echo ============================================
echo.

REM Proje dizini
set PROJE_DIZINI=%~dp0
set SCRIPT_YOLU=%PROJE_DIZINI%zamanlanmis_calistir.bat

echo Proje dizini: %PROJE_DIZINI%
echo Script yolu: %SCRIPT_YOLU%
echo.

REM Gorev adi
set GOREV_ADI=AIUyumlulukKutusu_Zamanlanmis

REM Mevcut gorevi sil (varsa)
echo Mevcut gorev kontrol ediliyor...
schtasks /Query /TN "%GOREV_ADI%" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Mevcut gorev bulundu, siliniyor...
    schtasks /Delete /TN "%GOREV_ADI%" /F >nul 2>&1
)

REM Yeni gorev olustur - her gun 09:00'da calissin
echo Yeni gorev olusturuluyor...
schtasks /Create ^
    /TN "%GOREV_ADI%" ^
    /TR "\"%SCRIPT_YOLU%\"" ^
    /SC DAILY ^
    /ST 09:00 ^
    /RL HIGHEST ^
    /F

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ BASARILI: Gorev olusturuldu!
    echo.
    echo Gorev adi: %GOREV_ADI%
    echo Calisma zamani: Her gun 09:00
    echo.
    echo Gorevi kontrol etmek icin:
    echo   schtasks /Query /TN "%GOREV_ADI%"
    echo.
    echo Gorevi silmek icin:
    echo   schtasks /Delete /TN "%GOREV_ADI%" /F
    echo.
    echo Gorevi manuel calistirmak icin:
    echo   schtasks /Run /TN "%GOREV_ADI%"
) else (
    echo.
    echo ❌ HATA: Gorev olusturulamadi!
    echo Yonetici olarak calistirdiginizdan emin olun.
)

echo.
pause