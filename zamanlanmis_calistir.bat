@echo off
REM AI Uyumluluk Kutusu - Zamanlanmis Denetim Calistirici
REM Windows Task Scheduler tarafindan cagirilir

cd /d "%~dp0"

REM Log dosyasi
set LOGFILE=%~dp0zamanlanmis_log.txt

echo. >> "%LOGFILE%"
echo ============================================ >> "%LOGFILE%"
echo Tarih: %date% %time% >> "%LOGFILE%"
echo ============================================ >> "%LOGFILE%"

py zamanlanmis_calistir.py >> "%LOGFILE%" 2>&1

echo. >> "%LOGFILE%"
echo Bitti: %date% %time% >> "%LOGFILE%"