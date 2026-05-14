import os
import numpy as np
import pandas as pd
import yfinance as yf
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from config import CACHE_DIR, ALL_TICKERS, TICKER_NAMES

_CACHE_FILE = os.path.join(CACHE_DIR, "prices.csv")


def _load_ticker_prices(ticker, period="2y"):
    if os.path.exists(_CACHE_FILE):
        df = pd.read_csv(_CACHE_FILE, index_col=0, parse_dates=True)
        if ticker in df.columns:
            return df[ticker].dropna()
    try:
        raw = yf.download(ticker, period=period, auto_adjust=True, progress=False)
        if isinstance(raw.columns, pd.MultiIndex):
            return raw["Close"][ticker].dropna()
        return raw["Close"].dropna()
    except Exception:
        return pd.Series(dtype=float)


def _compute_rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = (-delta.clip(upper=0)).rolling(period).mean()
    rs = gain / loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))


def prepare_features(prices_df, ticker):
    if ticker not in prices_df.columns:
        return pd.DataFrame()
    s = prices_df[ticker].dropna()

    df = pd.DataFrame(index=s.index)
    df["price"] = s
    df["ret_1d"] = s.pct_change(1)
    df["ret_5d"] = s.pct_change(5)
    df["ret_20d"] = s.pct_change(20)
    df["sma20"] = s.rolling(20).mean()
    df["sma50"] = s.rolling(50).mean()
    df["sma20_ratio"] = s / df["sma20"]
    df["sma50_ratio"] = s / df["sma50"]
    df["rsi14"] = _compute_rsi(s, 14)
    df["bb_mid"] = s.rolling(20).mean()
    df["bb_std"] = s.rolling(20).std()
    df["bb_pos"] = (s - df["bb_mid"]) / (2 * df["bb_std"])

    # MACD
    ema12 = s.ewm(span=12, adjust=False).mean()
    ema26 = s.ewm(span=26, adjust=False).mean()
    macd = ema12 - ema26
    signal = macd.ewm(span=9, adjust=False).mean()
    df["macd_hist"] = macd - signal

    return df.dropna()


def predict_direction(ticker, horizon_days=30):
    prices = _load_ticker_prices(ticker)
    if len(prices) < 120:
        return {
            "ticker": ticker,
            "name": TICKER_NAMES.get(ticker, ticker),
            "direction": "neutral",
            "confidence": 0.5,
            "feature_importance": {},
            "error": "Datos insuficientes",
        }

    try:
        df = pd.DataFrame({"price": prices})
        df["ret_1d"] = prices.pct_change(1)
        df["ret_5d"] = prices.pct_change(5)
        df["ret_20d"] = prices.pct_change(20)
        df["sma20"] = prices.rolling(20).mean()
        df["sma50"] = prices.rolling(50).mean()
        df["sma20_ratio"] = prices / df["sma20"]
        df["sma50_ratio"] = prices / df["sma50"]
        df["rsi14"] = _compute_rsi(prices, 14)
        ema12 = prices.ewm(span=12, adjust=False).mean()
        ema26 = prices.ewm(span=26, adjust=False).mean()
        macd = ema12 - ema26
        df["macd_hist"] = macd - macd.ewm(span=9, adjust=False).mean()
        df["bb_pos"] = (prices - prices.rolling(20).mean()) / (2 * prices.rolling(20).std())

        # Target: 1 if price in horizon_days > current price
        df["target"] = (prices.shift(-horizon_days) > prices).astype(int)
        df = df.dropna()

        if len(df) < 60:
            raise ValueError("Not enough rows after dropna")

        feature_cols = ["ret_1d", "ret_5d", "ret_20d", "sma20_ratio", "sma50_ratio",
                        "rsi14", "macd_hist", "bb_pos"]
        X = df[feature_cols].values
        y = df["target"].values

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
        scaler = StandardScaler()
        X_train_s = scaler.fit_transform(X_train)
        X_test_s = scaler.transform(X_test)

        model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
        model.fit(X_train_s, y_train)

        latest_features = scaler.transform(X[-1:])
        prob = model.predict_proba(latest_features)[0]
        direction = "up" if prob[1] >= 0.5 else "down"
        confidence = float(max(prob))

        importance = dict(zip(feature_cols, model.feature_importances_.round(3)))

        return {
            "ticker": ticker,
            "name": TICKER_NAMES.get(ticker, ticker),
            "direction": direction,
            "confidence": round(confidence, 3),
            "feature_importance": importance,
            "horizon_days": horizon_days,
        }
    except Exception as e:
        return {
            "ticker": ticker,
            "name": TICKER_NAMES.get(ticker, ticker),
            "direction": "neutral",
            "confidence": 0.5,
            "feature_importance": {},
            "error": str(e),
        }


def get_price_forecast(ticker, days=30):
    prices = _load_ticker_prices(ticker)
    if len(prices) < 30:
        return {
            "ticker": ticker,
            "current_price": None,
            "optimistic": None,
            "base": None,
            "pessimistic": None,
        }
    current = float(prices.iloc[-1])
    returns = prices.pct_change().dropna()
    daily_vol = float(returns.std())
    daily_drift = float(returns.mean())

    base = current * (1 + daily_drift * days)
    optimistic = current * (1 + daily_drift * days + 1.5 * daily_vol * np.sqrt(days))
    pessimistic = current * (1 + daily_drift * days - 1.5 * daily_vol * np.sqrt(days))

    return {
        "ticker": ticker,
        "name": TICKER_NAMES.get(ticker, ticker),
        "current_price": round(current, 2),
        "optimistic": round(optimistic, 2),
        "base": round(base, 2),
        "pessimistic": round(pessimistic, 2),
        "horizon_days": days,
    }


def get_predictions_summary(tickers=None):
    if tickers is None:
        tickers = ALL_TICKERS
    predictions = {}
    for ticker in tickers:
        direction_data = predict_direction(ticker)
        forecast_data = get_price_forecast(ticker)
        predictions[ticker] = {**direction_data, **forecast_data}
    return predictions
