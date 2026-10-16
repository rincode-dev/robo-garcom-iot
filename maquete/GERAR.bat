@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo Gerando a maquete (mesas, cadeiras, balcao) a partir de medidas.txt...
echo.
"..\carcaca\.venv\Scripts\python.exe" -W ignore gerar.py
echo.
pause
