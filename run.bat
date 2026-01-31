@echo off
echo ============================================================
echo    Dashboard Financeiro 2026
echo ============================================================
echo.

REM Ativa ambiente virtual se existir
if exist venv\Scripts\activate (
    call venv\Scripts\activate
    echo [OK] Ambiente virtual ativado
) else (
    echo [AVISO] Ambiente virtual nao encontrado.
    echo Execute setup.bat primeiro ou usando Python global.
)

echo.
echo Iniciando Dashboard...
echo.
echo Acesse: http://127.0.0.1:8050
echo Pressione Ctrl+C para parar
echo.

python app.py
