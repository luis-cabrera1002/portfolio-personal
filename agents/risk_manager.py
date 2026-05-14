import os
import numpy as np
import pandas as pd
from config import CACHE_DIR, ALL_TICKERS, TICKER_NAMES

_CACHE_FILE = os.path.join(CACHE_DIR, "prices.csv")


def _load_prices(tickers):
    if os.path.exists(_CACHE_FILE):
        df = pd.read_csv(_CACHE_FILE, index_col=0, parse_dates=True)
        cols = [t for t in tickers if t in df.columns]
        return df[cols].dropna(how="all") if cols else df.dropna(how="all")
    from agents.market_analyst import fetch_prices
    return fetch_prices(tickers)


def calculate_var(returns, confidence=0.95):
    clean = returns.dropna()
    if len(clean) == 0:
        return 0.0
    return float(np.percentile(clean, (1 - confidence) * 100))


def calculate_portfolio_risk(weights_dict, returns_df):
    tickers = [t for t in weights_dict if t in returns_df.columns]
    if not tickers:
        return {}

    w = np.array([weights_dict[t] for t in tickers])
    w = w / w.sum()  # normalise

    rets = returns_df[tickers].dropna()
    port_returns = rets @ w

    # Annualised metrics
    ann_vol = float(port_returns.std() * np.sqrt(252))
    ann_ret = float(port_returns.mean() * 252)

    var_95 = calculate_var(port_returns, 0.95)
    var_99 = calculate_var(port_returns, 0.99)
    cvar_95 = float(port_returns[port_returns <= var_95].mean()) if any(port_returns <= var_95) else var_95

    # Correlation — mean off-diagonal
    if len(tickers) > 1:
        corr_matrix = rets.corr()
        upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
        mean_corr = float(upper.stack().mean())
    else:
        mean_corr = 1.0

    # Herfindahl-Hirschman Index (concentration)
    hhi = float(np.sum(w ** 2))

    return {
        "annual_return": round(ann_ret, 4),
        "annual_volatility": round(ann_vol, 4),
        "var_95": round(var_95, 4),
        "var_99": round(var_99, 4),
        "cvar_95": round(cvar_95, 4),
        "mean_correlation": round(mean_corr, 3),
        "hhi_concentration": round(hhi, 3),
    }


def get_risk_alerts(metrics):
    alerts = []
    var95 = abs(metrics.get("var_95", 0))
    hhi = metrics.get("hhi_concentration", 0)
    vol = metrics.get("annual_volatility", 0)

    if var95 > 0.03:
        alerts.append({
            "level": "alto",
            "message": f"VaR diario al 95% es {var95:.2%} — supera el umbral del 3%. Considere reducir exposición o cubrir riesgo.",
        })
    if hhi > 0.25:
        alerts.append({
            "level": "medio",
            "message": f"Concentración HHI = {hhi:.2f} — portfolio poco diversificado. Distribuya mejor entre activos.",
        })
    if vol > 0.20:
        alerts.append({
            "level": "medio",
            "message": f"Volatilidad anualizada = {vol:.2%} — por encima del 20%. Revise exposición a activos de alta beta.",
        })
    if not alerts:
        alerts.append({
            "level": "bajo",
            "message": "Métricas de riesgo dentro de rangos aceptables.",
        })
    return alerts


def get_risk_summary(tickers=None, weights=None):
    if tickers is None:
        tickers = ALL_TICKERS
    prices_df = _load_prices(tickers)
    if prices_df.empty:
        return {"error": "No hay datos de precios disponibles."}

    returns_df = prices_df.pct_change().dropna()

    if weights is None:
        n = len([t for t in tickers if t in returns_df.columns])
        weights = {t: 1 / n for t in tickers if t in returns_df.columns}

    metrics = calculate_portfolio_risk(weights, returns_df)
    alerts = get_risk_alerts(metrics)

    # Per-ticker VaR
    per_ticker_var = {}
    for ticker in tickers:
        if ticker in returns_df.columns:
            per_ticker_var[ticker] = {
                "name": TICKER_NAMES.get(ticker, ticker),
                "var_95": round(calculate_var(returns_df[ticker], 0.95), 4),
                "volatility": round(float(returns_df[ticker].std() * np.sqrt(252)), 4),
            }

    # Correlation matrix
    valid = [t for t in tickers if t in returns_df.columns]
    corr_matrix = returns_df[valid].corr().round(3).to_dict() if valid else {}

    return {
        "portfolio_metrics": metrics,
        "alerts": alerts,
        "per_ticker_var": per_ticker_var,
        "correlation_matrix": corr_matrix,
    }
