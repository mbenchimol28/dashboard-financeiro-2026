@echo off
echo ============================================================
echo    Dashboard Financeiro 2026 - Setup
echo ============================================================
echo.

REM Verifica se Python 3.11 está instalado
python --version 2>nul | findstr /i "3.11" >nul
if %errorlevel% neq 0 (
    echo [ERRO] Python 3.11 nao encontrado!
    echo Por favor, instale Python 3.11 de https://python.org
    pause
    exit /b 1
)

echo [1/3] Criando ambiente virtual...
python -m venv venv
if %errorlevel% neq 0 (
    echo [ERRO] Falha ao criar ambiente virtual!
    pause
    exit /b 1
)

echo [2/3] Ativando ambiente virtual...
call venv\Scripts\activate

echo [3/3] Instalando dependencias...
pip install --upgrade pip
pip install -r requirements.txt

echo.
echo ============================================================
echo    Setup concluido com sucesso!
echo ============================================================
echo.
echo Para iniciar o dashboard, execute: run.bat
echo.
pause
