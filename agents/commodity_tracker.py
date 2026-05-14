import numpy as np
import pandas as pd
import yfinance as yf
from config import TICKER_NAMES

COMMODITY_TICKERS = ["GC=F", "CL=F", "SI=F", "NG=F"]


def get_commodity_data(period="3mo"):
    try:
        raw = yf.download(COMMODITY_TICKERS, period=period, auto_adjust=True, progress=False)
        if isinstance(raw.columns, pd.MultiIndex):
            df = raw["Close"]
        else:
            df = raw[["Close"]].rename(columns={"Close": COMMODITY_TICKERS[0]})
        return df.dropna(how="all")
    except Exception:
        return pd.DataFrame()


def _compute_rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = (-delta.clip(upper=0)).rolling(period).mean()
    rs = gain / loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))


def calculate_commodity_metrics(df):
    metrics = {}

    spy_series = None
    try:
        spy_raw = yf.download("SPY", period="3mo", auto_adjust=True, progress=False)
        if isinstance(spy_raw.columns, pd.MultiIndex):
            close = spy_raw["Close"]
            spy_series = close.iloc[:, 0].dropna() if isinstance(close, pd.DataFrame) else close.dropna()
        elif "Close" in spy_raw.columns:
            spy_series = spy_raw["Close"].dropna()
    except Exception:
        pass

    for ticker in df.columns:
        try:
            s = df[ticker].dropna()
            if len(s) < 10:
                continue
            current_price = float(s.iloc[-1])
            returns = s.pct_change().dropna()

            # Weekly & monthly change
            weekly_chg = float(s.pct_change(5).iloc[-1]) if len(s) >= 5 else 0.0
            monthly_chg = float(s.pct_change(21).iloc[-1]) if len(s) >= 21 else 0.0

            # Trend via SMA comparison
            sma20 = s.rolling(20).mean().iloc[-1] if len(s) >= 20 else s.mean()
            sma50 = s.rolling(50).mean().iloc[-1] if len(s) >= 50 else s.mean()
            if sma20 > sma50 * 1.01:
                trend = "alcista"
            elif sma20 < sma50 * 0.99:
                trend = "bajista"
            else:
                trend = "lateral"

            # Correlation with SPY
            corr_spy = None
            if spy_series is not None:
                r_al, spy_al = returns.align(spy_series.pct_change().dropna(), join="inner")
                if len(r_al) > 10:
                    corr_spy = round(float(r_al.corr(spy_al)), 3)

            metrics[ticker] = {
                "name": TICKER_NAMES.get(ticker, ticker),
                "current_price": round(current_price, 2),
                "weekly_change": round(weekly_chg, 4),
                "monthly_change": round(monthly_chg, 4),
                "trend": trend,
                "corr_spy": corr_spy,
                "sma20": round(float(sma20), 2),
                "sma50": round(float(sma50), 2),
            }
        except Exception:
            continue
    return metrics


def get_commodity_signals(df=None, metrics=None):
    if df is None:
        df = get_commodity_data()
    if metrics is None:
        metrics = calculate_commodity_metrics(df)

    signals = {}
    for ticker, m in metrics.items():
        trend = m.get("trend", "lateral")
        monthly = m.get("monthly_change", 0)
        rsi_val = None
        if ticker in df.columns:
            rsi_series = _compute_rsi(df[ticker].dropna())
            if not rsi_series.dropna().empty:
                rsi_val = float(rsi_series.dropna().iloc[-1])

        # Signal logic
        if trend == "alcista" and monthly > 0.02:
            signal = "COMPRAR"
            reason = "Tendencia alcista confirmada con momentum positivo."
        elif trend == "bajista" and monthly < -0.02:
            signal = "VENDER"
            reason = "Tendencia bajista con momentum negativo. Considere reducir exposición."
        elif rsi_val is not None and rsi_val > 70:
            signal = "VENDER"
            reason = f"RSI sobrecomprado ({rsi_val:.0f}). Posible corrección próxima."
        elif rsi_val is not None and rsi_val < 30:
            signal = "COMPRAR"
            reason = f"RSI sobrevendido ({rsi_val:.0f}). Oportunidad de entrada."
        else:
            signal = "MANTENER"
            reason = "Sin señal clara. Mantener posición actual."

        signals[ticker] = {
            "name": TICKER_NAMES.get(ticker, ticker),
            "signal": signal,
            "reason": reason,
            "rsi": round(rsi_val, 1) if rsi_val is not None else None,
            **{k: v for k, v in m.items() if k != "name"},
        }
    return signals


def get_summary():
    df = get_commodity_data()
    metrics = calculate_commodity_metrics(df)
    signals = get_commodity_signals(df, metrics)
    return {
        "prices_df": df,
        "metrics": metrics,
        "signals": signals,
        "commodities": signals,  # alias for smoke test compatibility
    }
