#!/bin/bash
echo "================================"
echo "  Iniciando Portfolio Personal  "
echo "================================"
echo ""
echo "Activando entorno..."
cd "$(dirname "$0")"

echo "Verificando dependencias..."
pip install -q feedparser schedule 2>/dev/null

echo "Iniciando Portfolio Personal..."
echo "Accede en: http://localhost:8501"
echo ""
streamlit run dashboard.py \
  --server.port 8501 \
  --server.headless true \
  --browser.gatherUsageStats false \
  --server.runOnSave true
