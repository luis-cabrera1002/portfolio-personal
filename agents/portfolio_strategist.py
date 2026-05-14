import os
import json
import re
import pandas as pd
import yfinance as yf
from pypfopt import EfficientFrontier, risk_models, expected_returns
from config import CACHE_DIR, TICKER_NAMES
from agents.ai_client import get_ai_response

_CACHE_FILE = os.path.join(CACHE_DIR, "prices.csv")


def _load_prices(tickers):
    if os.path.exists(_CACHE_FILE):
        df = pd.read_csv(_CACHE_FILE, index_col=0, parse_dates=True)
        cols = [t for t in tickers if t in df.columns]
        if cols:
            return df[cols].dropna(how="all")
    try:
        raw = yf.download(tickers, period="2y", auto_adjust=True, progress=False)
        return raw["Close"] if isinstance(raw.columns, pd.MultiIndex) else raw[["Close"]]
    except Exception:
        return pd.DataFrame()


def optimize_portfolio_full(tickers, method="max_sharpe"):
    prices = _load_prices(tickers)
    valid = [t for t in tickers if t in prices.columns] if not prices.empty else []

    if len(valid) < 2 or len(prices) < 100:
        n = max(len(tickers), 1)
        return {"weights": {t: round(1/n, 4) for t in tickers},
                "expected_return": 0.08, "volatility": 0.15,
                "sharpe_ratio": 0.23, "method": "equal_weight_fallback"}
    prices = prices[valid].dropna()
    try:
        mu = expected_returns.mean_historical_return(prices)
        S = risk_models.CovarianceShrinkage(prices).ledoit_wolf()
        ef = EfficientFrontier(mu, S)
        ef.min_volatility() if method == "min_volatility" else ef.max_sharpe(risk_free_rate=0.045)
        cleaned = ef.clean_weights()
        perf = ef.portfolio_performance(verbose=False, risk_free_rate=0.045)
        return {"weights": {k: round(v, 4) for k, v in cleaned.items() if v > 0.0005},
                "expected_return": round(perf[0], 4), "volatility": round(perf[1], 4),
                "sharpe_ratio": round(perf[2], 3), "method": method}
    except Exception as e:
        n = max(len(valid), 1)
        return {"weights": {t: round(1/n, 4) for t in valid},
                "expected_return": 0.08, "volatility": 0.15,
                "sharpe_ratio": 0.23, "method": "equal_weight_fallback", "error": str(e)}


def optimize_portfolio(tickers, method="max_sharpe"):
    return optimize_portfolio_full(tickers, method).get("weights", {})


def generate_recommendation(portfolio_metrics, esg_report, news_sentiment, macro_analysis, risk_metrics):
    def _t(obj, limit=1200):
        return str(obj)[:limit]

    context = (
        f"Portfolio & Allocation: {_t(portfolio_metrics)}\n\n"
        f"ESG Report: {_t(esg_report)}\n\n"
        f"News Sentiment: {_t(news_sentiment)}\n\n"
        f"Macro Analysis: {_t(macro_analysis)}\n\n"
        f"Risk Metrics: {_t(risk_metrics)}"
    )
    prompt = f"""Eres un analista de portafolio senior. Basándote en estos datos:

{context}

Genera recomendaciones específicas. Para cada activo del universo que aparezca, indica:
- action: COMPRAR | MANTENER | VENDER
- justification: 2-3 líneas basadas en los datos
- target_weight: peso sugerido como número decimal (ej. 0.12)

Responde SOLO en JSON válido con este formato exacto:
{{
  "recommendations": {{
    "TICKER": {{
      "action": "COMPRAR",
      "justification": "...",
      "target_weight": 0.10
    }}
  }},
  "overall_outlook": "resumen en 2 oraciones",
  "key_risks": ["riesgo1", "riesgo2"],
  "key_opportunities": ["oportunidad1", "oportunidad2"]
}}"""

    content = get_ai_response(prompt, max_tokens=2000)
    match = re.search(r"\{.*\}", content, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except Exception:
            pass
    return {"recommendations": {}, "overall_outlook": content[:300],
            "key_risks": [], "key_opportunities": []}


def get_strategy_summary(tickers, extra_data=None):
    allocation = optimize_portfolio_full(tickers)
    result = {"allocation": allocation, "recommendations": None}
    if extra_data:
        result["recommendations"] = generate_recommendation(
            extra_data.get("market", {}), extra_data.get("esg", {}),
            extra_data.get("news", []), extra_data.get("macro", {}),
            extra_data.get("risk", {}),
        )
    return result
