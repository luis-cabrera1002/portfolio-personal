import yfinance as yf
import pandas as pd
import json
import os
from datetime import datetime, timedelta
from config import CACHE_DIR, DEFAULT_LOOKBACK_DAYS


class DataIngestor:
    def __init__(self):
        os.makedirs(CACHE_DIR, exist_ok=True)

    def fetch_prices(self, tickers: list[str], days: int = DEFAULT_LOOKBACK_DAYS) -> pd.DataFrame:
        end = datetime.today()
        start = end - timedelta(days=days)
        data = yf.download(tickers, start=start, end=end, auto_adjust=True, progress=False)
        if isinstance(data.columns, pd.MultiIndex):
            return data["Close"]
        return data[["Close"]].rename(columns={"Close": tickers[0]})

    def fetch_ticker_info(self, ticker: str) -> dict:
        cache_path = os.path.join(CACHE_DIR, f"{ticker}_info.json")
        if os.path.exists(cache_path):
            mtime = os.path.getmtime(cache_path)
            if datetime.now().timestamp() - mtime < 86400:
                with open(cache_path) as f:
                    return json.load(f)
        info = yf.Ticker(ticker).info
        with open(cache_path, "w") as f:
            json.dump(info, f)
        return info

    def fetch_financials(self, ticker: str) -> dict:
        t = yf.Ticker(ticker)
        return {
            "income_stmt": t.financials.to_dict() if t.financials is not None else {},
            "balance_sheet": t.balance_sheet.to_dict() if t.balance_sheet is not None else {},
            "cash_flow": t.cashflow.to_dict() if t.cashflow is not None else {},
        }
