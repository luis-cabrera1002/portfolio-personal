import numpy as np
import pandas as pd
from datetime import datetime, timedelta

from agents.market_analyst import fetch_prices


def run_backtest(tickers, weights, start_date=None, end_date=None, benchmark="SPY"):
    if end_date is None:
        end_date = datetime.now().strftime("%Y-%m-%d")
    if start_date is None:
        start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")

    all_tickers = list({*tickers, benchmark})
    prices = fetch_prices(all_tickers, period="2y")

    if prices.empty:
        return {"error": "No se pudieron obtener precios históricos"}

    prices.index = pd.to_datetime(prices.index)
    prices = prices[start_date:end_date]

    if len(prices) < 20:
        return {"error": "Período demasiado corto para backtesting (mínimo 20 días)"}

    valid_tickers = [t for t in tickers if t in prices.columns]
    if not valid_tickers:
        return {"error": "Ningún ticker válido para backtesting"}

    total_w = sum(weights.get(t, 0) for t in valid_tickers)
    if total_w == 0:
        norm_weights = {t: 1 / len(valid_tickers) for t in valid_tickers}
    else:
        norm_weights = {t: weights.get(t, 0) / total_w for t in valid_tickers}

    price_subset = prices[valid_tickers].dropna()
    daily_returns = price_subset.pct_change().dropna()
    w_array = np.array([norm_weights.get(t, 0) for t in valid_tickers])
    portfolio_returns = (daily_returns * w_array).sum(axis=1)

    bench_returns = None
    bench_cum = None
    if benchmark in prices.columns:
        bench_col = prices[benchmark].dropna()
        bench_col = bench_col[bench_col.index.isin(portfolio_returns.index)]
        bench_returns = bench_col.pct_change().dropna()
        bench_returns = bench_returns[bench_returns.index.isin(portfolio_returns.index)]
        portfolio_returns = portfolio_returns[portfolio_returns.index.isin(bench_returns.index)]

    port_cum = (1 + portfolio_returns).cumprod()
    n_days   = len(portfolio_returns)
    ann_ret  = float(port_cum.iloc[-1] ** (252 / n_days)) - 1
    ann_vol  = float(portfolio_returns.std() * np.sqrt(252))
    sharpe   = (ann_ret - 0.045) / ann_vol if ann_vol > 0 else 0.0

    peak = float(port_cum.iloc[0])
    max_dd = 0.0
    for v in port_cum:
        if float(v) > peak:
            peak = float(v)
        dd = (float(v) - peak) / peak
        if dd < max_dd:
            max_dd = dd

    total_ret = round(float(port_cum.iloc[-1]) - 1, 4)
    result = {
        "start_date": str(price_subset.index[0])[:10],
        "end_date":   str(price_subset.index[-1])[:10],
        "portfolio": {
            "total_return":            total_ret,
            "total_return_pct":        round(total_ret * 100, 2),
            "annualized_return":       round(ann_ret, 4),
            "annualized_volatility":   round(ann_vol, 4),
            "sharpe_ratio":            round(sharpe, 3),
            "max_drawdown":            round(max_dd, 4),
        },
        "cumulative_returns": {
            "dates":     [str(d)[:10] for d in port_cum.index],
            "portfolio": [round(float(v), 4) for v in port_cum.values],
        },
        "weights_used": norm_weights,
    }

    if bench_returns is not None:
        bench_cum = (1 + bench_returns).cumprod()
        bench_ann_ret = float(bench_cum.iloc[-1] ** (252 / len(bench_returns))) - 1
        bench_vol     = float(bench_returns.std() * np.sqrt(252))
        bench_sharpe  = (bench_ann_ret - 0.045) / bench_vol if bench_vol > 0 else 0.0
        bench_total   = round(float(bench_cum.iloc[-1]) - 1, 4)

        # Beta of portfolio vs benchmark
        aligned_p = portfolio_returns[portfolio_returns.index.isin(bench_returns.index)]
        aligned_b = bench_returns[bench_returns.index.isin(aligned_p.index)]
        beta = 0.0
        if len(aligned_b) > 5:
            bench_var = float(np.var(aligned_b))
            if bench_var > 0:
                beta = round(float(np.cov(aligned_p, aligned_b)[0][1] / bench_var), 3)

        alpha_val = round(ann_ret - bench_ann_ret, 4)
        result["benchmark"] = {
            "ticker":                  benchmark,
            "total_return":            bench_total,
            "total_return_pct":        round(bench_total * 100, 2),
            "annualized_return":       round(bench_ann_ret, 4),
            "annualized_volatility":   round(bench_vol, 4),
            "sharpe_ratio":            round(bench_sharpe, 3),
        }
        result["alpha"]          = alpha_val
        result["alpha_pct"]      = round(alpha_val * 100, 2)
        result["beta"]           = beta
        result["outperformance"] = round(float(port_cum.iloc[-1]) - float(bench_cum.iloc[-1]), 4)
        result["cumulative_returns"]["benchmark"] = [round(float(v), 4) for v in bench_cum.values]

    return result


def get_monthly_returns_table(tickers, weights, period="1y"):
    prices = fetch_prices(tickers, period=period)
    if prices.empty:
        return pd.DataFrame()

    valid_tickers = [t for t in tickers if t in prices.columns]
    if not valid_tickers:
        return pd.DataFrame()

    total_w = sum(weights.get(t, 0) for t in valid_tickers)
    if total_w == 0:
        norm_weights = {t: 1 / len(valid_tickers) for t in valid_tickers}
    else:
        norm_weights = {t: weights.get(t, 0) / total_w for t in valid_tickers}

    price_subset = prices[valid_tickers].dropna()
    daily_returns = price_subset.pct_change().dropna()
    w_array = np.array([norm_weights.get(t, 0) for t in valid_tickers])
    portfolio_returns = (daily_returns * w_array).sum(axis=1)

    portfolio_returns.index = pd.to_datetime(portfolio_returns.index)
    monthly = portfolio_returns.resample("ME").apply(lambda x: float((1 + x).prod()) - 1)

    return pd.DataFrame({
        "Mes":         [d.strftime("%Y-%m") for d in monthly.index],
        "Retorno":     [f"{v:.2%}" for v in monthly.values],
        "Retorno_num": monthly.values,
    })
