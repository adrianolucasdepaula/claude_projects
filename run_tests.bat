@echo off
REM Script para executar testes E2E da GUI

echo ================================================
echo   Portfolio Analysis - Testes E2E
echo ================================================
echo.

REM Verificar se pytest e playwright estão instalados
py -m pytest --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] pytest nao encontrado!
    echo.
    echo Instalando dependencias de teste...
    py -m pip install pytest pytest-playwright
    py -m playwright install chromium
    echo.
)

echo.
echo IMPORTANTE: Certifique-se de que a aplicacao Streamlit esta rodando!
echo Execute em outro terminal: run_gui.bat
echo Ou: py -m streamlit run app.py
echo.
echo Pressione qualquer tecla para continuar os testes...
pause >nul

echo.
echo Executando testes E2E...
echo ================================================
echo.

py -m pytest tests/test_gui_playwright.py -v --headed --tb=short

echo.
echo ================================================
echo Testes concluidos!
echo ================================================
echo.

pause
