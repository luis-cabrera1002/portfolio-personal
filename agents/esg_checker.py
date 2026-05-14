import yfinance as yf
from config import TICKER_NAMES

# Reference ESG scores (0-100) used when yfinance sustainability data is unavailable
_ESG_BASELINE = {
    "AAPL":  {"environmental": 75, "social": 72, "governance": 78},
    "NVDA":  {"environmental": 62, "social": 60, "governance": 64},
    "MSFT":  {"environmental": 80, "social": 78, "governance": 82},
    "AMZN":  {"environmental": 58, "social": 55, "governance": 62},
    "TSLA":  {"environmental": 55, "social": 52, "governance": 58},
    "BRK-B": {"environmental": 48, "social": 50, "governance": 55},
    "GOOGL": {"environmental": 72, "social": 68, "governance": 74},
    "META":  {"environmental": 50, "social": 45, "governance": 52},
    "JPM":   {"environmental": 65, "social": 62, "governance": 68},
    "V":     {"environmental": 70, "social": 67, "governance": 72},
    # Commodities & ETFs — proxy scores
    "GC=F":  {"environmental": 40, "social": 38, "governance": 45},
    "CL=F":  {"environmental": 25, "social": 35, "governance": 40},
    "SI=F":  {"environmental": 38, "social": 36, "governance": 43},
    "NG=F":  {"environmental": 32, "social": 37, "governance": 41},
    "SPY":   {"environmental": 65, "social": 62, "governance": 68},
    "QQQ":   {"environmental": 68, "social": 65, "governance": 70},
    "GLD":   {"environmental": 42, "social": 40, "governance": 47},
    "TLT":   {"environmental": 60, "social": 58, "governance": 65},
    "IBIT":  {"environmental": 30, "social": 35, "governance": 40},
}

_THRESHOLDS = {"environmental": 50, "social": 45, "governance": 55}


def get_esg_scores(tickers):
    scores = {}
    for ticker in tickers:
        base = _ESG_BASELINE.get(ticker, {"environmental": 50, "social": 50, "governance": 50})
        try:
            t = yf.Ticker(ticker)
            sus = t.sustainability
            if sus is not None and not sus.empty:
                data = sus.get("Value", sus.iloc[:, 0])
                e = float(data.get("environmentScore", base["environmental"]) or base["environmental"])
                s = float(data.get("socialScore", base["social"]) or base["social"])
                g = float(data.get("governanceScore", base["governance"]) or base["governance"])
                # yfinance returns scores 0-10; normalize to 0-100 if needed
                if e <= 10:
                    e, s, g = e * 10, s * 10, g * 10
                scores[ticker] = {"environmental": round(e, 1), "social": round(s, 1), "governance": round(g, 1)}
                continue
        except Exception:
            pass
        scores[ticker] = base.copy()
    return scores


def check_compliance(ticker, scores):
    s = scores.get(ticker, {})
    issues = []
    for dimension, threshold in _THRESHOLDS.items():
        if s.get(dimension, 0) < threshold:
            issues.append(f"{dimension.capitalize()} score ({s.get(dimension, 0)}) por debajo del umbral mínimo ({threshold})")
    return len(issues) == 0, issues


def get_esg_report(tickers):
    scores = get_esg_scores(tickers)
    report = {}
    for ticker in tickers:
        s = scores.get(ticker, {"environmental": 50, "social": 50, "governance": 50})
        e, so, g = s["environmental"], s["social"], s["governance"]
        total = round((e + so + g) / 3, 1)
        compliant, issues = check_compliance(ticker, scores)

        if total >= 65:
            traffic_light = "verde"
        elif total >= 50:
            traffic_light = "amarillo"
        else:
            traffic_light = "rojo"

        report[ticker] = {
            "name": TICKER_NAMES.get(ticker, ticker),
            "environmental_score": e,
            "social_score": so,
            "governance_score": g,
            "total_score": total,
            "compliant": compliant,
            "traffic_light": traffic_light,
            "issues": issues,
        }
    return report
