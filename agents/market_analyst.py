import os
import numpy as np
import pandas as pd
import yfinance as yf
from config import CACHE_DIR, ALL_TICKERS, TICKER_NAMES

os.makedirs(CACHE_DIR, exist_ok=True)
RISK_FREE_RATE = 0.045
_CACHE_FILE = os.path.join(CACHE_DIR, "prices.csv")


def fetch_prices(tickers=None, period="1y"):
    if tickers is None:
        tickers = ALL_TICKERS
    try:
        raw = yf.download(tickers, period=period, auto_adjust=True, progress=False)
        if isinstance(raw.columns, pd.MultiIndex):
            df = raw["Close"]
        elif "Close" in raw.columns:
            name = tickers[0] if isinstance(tickers, list) else tickers
            df = raw[["Close"]].rename(columns={"Close": name})
        else:
            df = raw
        df = df.dropna(how="all")
        df.index = pd.to_datetime(df.index)
        df.to_csv(_CACHE_FILE)
        return df
    except Exception:
        if os.path.exists(_CACHE_FILE):
            return pd.read_csv(_CACHE_FILE, index_col=0, parse_dates=True)
        return pd.DataFrame()


def calculate_metrics(df):
    metrics = {}
    spy_returns = df["SPY"].pct_change(fill_method=None).dropna() if "SPY" in df.columns else None

    for ticker in df.columns:
        try:
            prices = df[ticker].dropna()
            if len(prices) < 10:
                continue
            returns = prices.pct_change().dropna()
            total_return = float((prices.iloc[-1] / prices.iloc[0]) - 1)
            n_years = max(len(prices) / 252, 0.01)
            ann_return = float((1 + total_return) ** (1 / n_years) - 1)
            volatility = float(returns.std() * np.sqrt(252))
            sharpe = (ann_return - RISK_FREE_RATE) / volatility if volatility > 0 else 0.0

            cum = (1 + returns).cumprod()
            rolling_max = cum.cummax()
            max_drawdown = float(((cum - rolling_max) / rolling_max).min())

            beta = None
            if spy_returns is not None and ticker != "SPY":
                r_al, s_al = returns.align(spy_returns, join="inner")
                if len(r_al) > 10:
                    spy_var = float(np.var(s_al))
                    if spy_var > 0:
                        beta = float(np.cov(r_al, s_al)[0][1] / spy_var)

            metrics[ticker] = {
                "name": TICKER_NAMES.get(ticker, ticker),
                "total_return": round(total_return, 4),
                "total_return_pct": round(total_return * 100, 2),
                "annualized_return": round(ann_return, 4),
                "volatility": round(volatility, 4),
                "sharpe_ratio": round(sharpe, 3),
                "sharpe": round(sharpe, 3),
                "max_drawdown": round(max_drawdown, 4),
                "beta": round(beta, 3) if beta is not None else None,
            }
        except Exception:
            continue
    return metrics


def get_current_prices(tickers=None):
    if tickers is None:
        tickers = ALL_TICKERS
    result = {}
    for ticker in tickers:
        try:
            fi = yf.Ticker(ticker).fast_info
            current = float(fi.last_price)
            prev = float(fi.previous_close)
            change_pct = ((current - prev) / prev * 100) if prev > 0 else 0.0
            result[ticker] = {
                "name": TICKER_NAMES.get(ticker, ticker),
                "price": round(current, 2),
                "change_pct": round(change_pct, 2),
                "volume": getattr(fi, "three_month_average_volume", None),
            }
        except Exception:
            result[ticker] = {
                "name": TICKER_NAMES.get(ticker, ticker),
                "price": None,
                "change_pct": 0.0,
                "volume": None,
            }
    return result


def get_summary(tickers=None):
    if tickers is None:
        tickers = ALL_TICKERS
    df = fetch_prices(tickers)
    metrics = calculate_metrics(df) if not df.empty else {}
    current_prices = get_current_prices(tickers)
    return {
        "prices_df": df,
        "metrics": metrics,
        "current_prices": current_prices,
    }
