@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo Gerando a carcaca a partir de medidas.txt...
echo.
".venv\Scripts\python.exe" -W ignore gerar.py
echo.
echo Montando o prototipo demonstrativo (robo completo com eletronica e fios)...
".venv\Scripts\python.exe" -W ignore prototipo.py
echo.
pause
