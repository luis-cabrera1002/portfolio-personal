import os
from dotenv import load_dotenv

load_dotenv()

NEWS_API_KEY      = os.environ.get("NEWS_API_KEY")      or os.getenv("NEWS_API_KEY",      "")
FRED_API_KEY      = os.environ.get("FRED_API_KEY")      or os.getenv("FRED_API_KEY",      "")
ALPHA_VANTAGE_KEY = os.environ.get("ALPHA_VANTAGE_KEY") or os.getenv("ALPHA_VANTAGE_KEY", "")

UNIVERSE = {
    "stocks": ["AAPL", "NVDA", "MSFT", "AMZN", "TSLA", "BRK-B", "GOOGL", "META", "JPM", "V"],
    "commodities": ["GC=F", "CL=F", "SI=F", "NG=F"],
    "etfs": ["SPY", "QQQ", "GLD", "TLT", "IBIT"],
}

ALL_TICKERS = (
    UNIVERSE["stocks"]
    + UNIVERSE["commodities"]
    + UNIVERSE["etfs"]
)

TICKER_NAMES = {
    "AAPL": "Apple",
    "NVDA": "Nvidia",
    "MSFT": "Microsoft",
    "AMZN": "Amazon",
    "TSLA": "Tesla",
    "BRK-B": "Berkshire Hathaway",
    "GOOGL": "Alphabet",
    "META": "Meta",
    "JPM": "JPMorgan",
    "V": "Visa",
    "GC=F": "Oro",
    "CL=F": "Petróleo WTI",
    "SI=F": "Plata",
    "NG=F": "Gas Natural",
    "SPY": "S&P 500 ETF",
    "QQQ": "Nasdaq ETF",
    "GLD": "Gold ETF",
    "TLT": "Bonds ETF",
    "IBIT": "Bitcoin ETF",
}

CACHE_DIR = "data/cache"
UPLOAD_DIR = "data/uploads"
REPORTS_DIR = "reports"

GOOGLE_API_KEY    = os.environ.get("GOOGLE_API_KEY")    or os.getenv("GOOGLE_API_KEY",    "")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY") or os.getenv("ANTHROPIC_API_KEY", "")
GEMINI_MODEL      = os.environ.get("GEMINI_MODEL",      "gemini-2.5-flash")
AI_PROVIDER       = "gemini"

APP_TITLE    = os.environ.get("APP_TITLE")    or os.getenv("APP_TITLE",    "Portfolio Personal")
APP_SUBTITLE = os.environ.get("APP_SUBTITLE") or os.getenv("APP_SUBTITLE", "Mi Centro de Inteligencia Financiera")
APP_ICON     = os.environ.get("APP_ICON")     or os.getenv("APP_ICON",     "🧠")
