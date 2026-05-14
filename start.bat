@echo off
echo ================================
echo   Iniciando Portfolio Personal
echo ================================
echo.
cd /d "%~dp0"
echo Iniciando Portfolio Personal...
echo Accede en: http://localhost:8501
echo.
streamlit run dashboard.py --server.port 8501 --server.headless true --browser.gatherUsageStats false --server.runOnSave true
