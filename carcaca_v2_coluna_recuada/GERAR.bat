@echo off
chcp 65001 >nul
cd /d "%~dp0"
rem Versao 2 (coluna recuada): usa o mesmo Python/CadQuery da pasta carcaca
echo Gerando a carcaca VERSAO 2 (coluna recuada) a partir de medidas.txt...
echo.
"..\carcaca\.venv\Scripts\python.exe" -W ignore gerar.py
echo.
echo Montando o prototipo demonstrativo (robo completo com eletronica e fios)...
"..\carcaca\.venv\Scripts\python.exe" -W ignore prototipo.py
echo.
pause
