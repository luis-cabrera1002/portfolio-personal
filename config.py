import os
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")
FRED_API_KEY = os.getenv("FRED_API_KEY", "")
ALPHA_VANTAGE_KEY = os.getenv("ALPHA_VANTAGE_KEY", "")

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

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
AI_PROVIDER = "gemini"  # opciones: "gemini" o "anthropic"
GEMINI_MODEL = "models/gemini-2.5-flash"  # usar nombre completo con prefijo models/

APP_TITLE    = os.getenv("APP_TITLE",    "Portfolio Personal")
APP_SUBTITLE = os.getenv("APP_SUBTITLE", "Mi Centro de Inteligencia Financiera")
APP_ICON     = os.getenv("APP_ICON",     "🧠")
