@echo off
rem Klava: install for current user (Start menu shortcut). Add -Desktop for a desktop shortcut.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0packaging\windows.ps1" %*
pause
