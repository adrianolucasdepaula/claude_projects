@echo off
REM Script para iniciar a interface web do Portfolio Analysis

echo ================================================
echo   Portfolio Analysis - Interface Web
echo ================================================
echo.

REM Verificar se Streamlit está instalado
py -m streamlit --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Streamlit nao encontrado!
    echo.
    echo Instalando dependencias...
    py -m pip install -r requirements.txt
    echo.
)

echo Iniciando aplicacao Streamlit...
echo.
echo Acesse no navegador: http://localhost:8501
echo.
echo Pressione Ctrl+C para parar o servidor
echo ================================================
echo.

py -m streamlit run app.py

pause
