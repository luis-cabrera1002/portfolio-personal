# Portfolio Intelligence

Sistema multi-agente de análisis de portafolio de inversiones impulsado por Claude AI.

## Agentes

| Agente | Función |
|--------|---------|
| `DataIngestor` | Descarga precios históricos e información de activos via yfinance |
| `MarketAnalyst` | Análisis fundamental y técnico de activos |
| `ESGChecker` | Evaluación de criterios ambientales, sociales y de gobernanza |
| `NewsSentinel` | Monitoreo de noticias y análisis de sentimiento |
| `PortfolioStrategist` | Optimización de portafolio (Sharpe, mínima volatilidad) |
| `PredictorEngine` | Predicciones ML con Random Forest |
| `RiskManager` | VaR, CVaR, drawdown y stress testing |
| `DocumentIntelligence` | Análisis de reportes PDF y documentos financieros |
| `MacroMonitor` | Indicadores macroeconómicos via FRED API |
| `CommodityTracker` | Seguimiento de materias primas |
| `ReportGenerator` | Generación de reportes PDF ejecutivos |

## Instalación

```bash
cd portfolio-intelligence
pip install -r requirements.txt
cp .env.example .env
# Edita .env con tus API keys
```

## Uso

### Dashboard interactivo
```bash
streamlit run dashboard.py
```

### Análisis programático
```python
from orchestrator import Orchestrator

orch = Orchestrator()
results = orch.run_full_analysis(["AAPL", "NVDA", "MSFT"])
print(results["executive_summary"])
```

## Variables de entorno

| Variable | Descripción | Requerida |
|----------|-------------|-----------|
| `ANTHROPIC_API_KEY` | Clave API de Anthropic | Sí |
| `NEWS_API_KEY` | Clave NewsAPI.org | Opcional |
| `FRED_API_KEY` | Clave Federal Reserve FRED | Opcional |
| `ALPHA_VANTAGE_KEY` | Clave Alpha Vantage | Opcional |
