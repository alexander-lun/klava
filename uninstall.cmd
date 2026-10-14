@echo off
rem Klava: uninstall
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0packaging\windows.ps1" -Uninstall
pause
