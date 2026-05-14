from config import FRED_API_KEY
from agents.ai_client import get_ai_response

# Updated 2026 baseline values used as intelligent fallback
_HARDCODED_MACRO = {
    "fed_funds_rate":     {"value": 4.25, "unit": "%", "label": "Tasa Fed Funds"},
    "cpi_yoy":            {"value": 3.2,  "unit": "%", "label": "Inflación CPI (YoY)"},
    "unemployment_rate":  {"value": 4.1,  "unit": "%", "label": "Tasa de Desempleo"},
    "gdp_growth_qoq":     {"value": 2.8,  "unit": "%", "label": "Crecimiento PIB (QoQ ann.)"},
    "10y_treasury":       {"value": 4.45, "unit": "%", "label": "Bono Tesoro 10 años"},
    "yield_spread_2y10y": {"value": 0.30, "unit": "%", "label": "Spread 2Y-10Y"},
}

_FRED_SERIES = {
    "fed_funds_rate":    "FEDFUNDS",
    "cpi_yoy":           "CPIAUCSL",
    "unemployment_rate": "UNRATE",
    "gdp_growth_qoq":    "A191RL1Q225SBEA",
}


def _fetch_rates_yfinance(data):
    """Try to get live interest rate data from yfinance treasury tickers."""
    try:
        import yfinance as yf
        import pandas as pd

        # 10-year treasury yield (^TNX quotes in percentage points)
        tnx = yf.Ticker("^TNX")
        tnx_info = tnx.fast_info
        if hasattr(tnx_info, "last_price") and tnx_info.last_price:
            data["10y_treasury"]["value"] = round(float(tnx_info.last_price), 2)

        # 2-year treasury for spread calc
        twoyr = yf.Ticker("^IRX")  # 13-week proxy
        twoyr_info = twoyr.fast_info
        if hasattr(twoyr_info, "last_price") and twoyr_info.last_price:
            rate_2y = round(float(twoyr_info.last_price) / 100, 4) * 100
            spread = round(data["10y_treasury"]["value"] - rate_2y, 2)
            data["yield_spread_2y10y"]["value"] = spread
    except Exception:
        pass
    return data


def _fetch_cpi_bls(data):
    """Attempt to fetch latest CPI from BLS public API (no key required)."""
    try:
        import requests
        resp = requests.post(
            "https://api.bls.gov/publicAPI/v2/timeseries/data/",
            json={"seriesid": ["CPIAUCSL"], "startyear": "2025", "endyear": "2026"},
            headers={"Content-type": "application/json"},
            timeout=6,
        )
        if resp.status_code == 200:
            series_list = resp.json().get("Results", {}).get("series", [])
            if series_list:
                items = series_list[0].get("data", [])
                if len(items) >= 13:
                    # Calculate YoY: latest vs same month prior year
                    latest_val   = float(items[0]["value"])
                    year_ago_val = float(items[12]["value"])
                    yoy = round((latest_val / year_ago_val - 1) * 100, 2)
                    data["cpi_yoy"]["value"] = yoy
                    data["cpi_yoy"]["date"]  = f"{items[0]['year']}-{items[0]['period'].replace('M','')}"
    except Exception:
        pass
    return data


def fetch_fred_data():
    data = {k: dict(v) for k, v in _HARDCODED_MACRO.items()}  # deep copy

    # Attempt real-time data (non-blocking; falls back gracefully)
    data = _fetch_rates_yfinance(data)
    data = _fetch_cpi_bls(data)

    # FRED API (most accurate if key present)
    if FRED_API_KEY:
        try:
            from fredapi import Fred
            fred = Fred(api_key=FRED_API_KEY)
            for key, series_id in _FRED_SERIES.items():
                try:
                    series = fred.get_series(series_id).dropna()
                    if not series.empty:
                        data[key] = {
                            "value": round(float(series.iloc[-1]), 2),
                            "unit":  "%",
                            "label": _HARDCODED_MACRO[key]["label"],
                            "date":  str(series.index[-1])[:10],
                        }
                except Exception:
                    continue
        except Exception:
            pass

    return data


def analyze_macro_impact(macro_data):
    lines = [
        f"- {info.get('label', k)}: {info.get('value', 'N/A')}{info.get('unit', '')}"
        for k, info in macro_data.items()
        if isinstance(info, dict)
    ]
    prompt = (
        "Dado este entorno macroeconómico:\n" + "\n".join(lines) + "\n\n"
        "Analiza en 3 párrafos cortos: "
        "1) impacto en acciones tech, "
        "2) impacto en commodities, "
        "3) recomendación de posicionamiento. "
        "Sé específico y directo."
    )
    return get_ai_response(prompt, max_tokens=500)


def get_macro_summary():
    macro_data = fetch_fred_data()
    return {"indicators": macro_data, "analysis": analyze_macro_impact(macro_data)}
