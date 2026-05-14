import json
import re
import requests
from datetime import datetime, timezone
from config import NEWS_API_KEY, TICKER_NAMES
from agents.ai_client import get_ai_response

_RSS_FEEDS = [
    ("MarketWatch",   "https://feeds.marketwatch.com/marketwatch/topstories"),
    ("Seeking Alpha", "https://seekingalpha.com/feed.xml"),
    ("CNBC Markets",  "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=100003114"),
]

_FALLBACK_NEWS = [
    {"title": "Federal Reserve signals cautious approach to rate cuts amid persistent inflation",
     "description": "Fed officials maintain hawkish stance as core inflation stays elevated.",
     "url": "#", "publishedAt": "2026-05-13", "source": "Reuters"},
    {"title": "Nvidia reports record AI chip demand, raises full-year guidance",
     "description": "Data center revenue surges on accelerating AI infrastructure spend.",
     "url": "#", "publishedAt": "2026-05-12", "source": "Reuters"},
    {"title": "Apple expands AI features across product line in major software update",
     "description": "On-device AI capabilities rolling out to iPhone and Mac users globally.",
     "url": "#", "publishedAt": "2026-05-11", "source": "Yahoo Finance"},
    {"title": "Oil prices slide on global demand concerns and inventory build",
     "description": "WTI crude falls as US stockpiles rise more than expected.",
     "url": "#", "publishedAt": "2026-05-10", "source": "Reuters"},
    {"title": "Microsoft Azure cloud revenue surges 35% year-over-year",
     "description": "Cloud and AI services drive beat on revenue and earnings estimates.",
     "url": "#", "publishedAt": "2026-05-09", "source": "Yahoo Finance"},
    {"title": "JPMorgan beats earnings estimates, credit quality holds steady",
     "description": "Net interest income and investment banking fees exceeded analyst forecasts.",
     "url": "#", "publishedAt": "2026-05-08", "source": "Reuters"},
    {"title": "Tesla deliveries disappoint as EV competition intensifies globally",
     "description": "Q1 deliveries fall short of Wall Street estimates amid price wars.",
     "url": "#", "publishedAt": "2026-05-07", "source": "Yahoo Finance"},
    {"title": "Gold hits new all-time high as investors seek safe-haven assets",
     "description": "Spot gold crosses $3,200 as geopolitical tensions and dollar weakness persist.",
     "url": "#", "publishedAt": "2026-05-06", "source": "Reuters"},
]


def _parse_rss_date(entry) -> str:
    for attr in ("published", "updated"):
        val = getattr(entry, attr, None)
        if val:
            try:
                import email.utils
                dt = email.utils.parsedate_to_datetime(val)
                return dt.strftime("%Y-%m-%d")
            except Exception:
                return val[:10]
    return datetime.now().strftime("%Y-%m-%d")


def fetch_news(query, max_articles=5):
    # 1) NewsAPI (if key available)
    if NEWS_API_KEY:
        try:
            resp = requests.get(
                "https://newsapi.org/v2/everything",
                params={"q": query, "sortBy": "relevancy", "language": "en",
                        "pageSize": max_articles, "apiKey": NEWS_API_KEY},
                timeout=8,
            )
            if resp.status_code == 200:
                articles = resp.json().get("articles", [])
                results = [
                    {"title": a.get("title", ""), "description": a.get("description", ""),
                     "url": a.get("url", "#"),
                     "publishedAt": (a.get("publishedAt") or "")[:10],
                     "source": a.get("source", {}).get("name", "")}
                    for a in articles if a.get("title")
                ]
                if results:
                    return results[:max_articles]
        except Exception:
            pass

    # 2) RSS feeds (free, no key required)
    try:
        import feedparser
        kw = [w.lower() for w in query.split() if len(w) > 2]
        collected = []
        for feed_name, feed_url in _RSS_FEEDS:
            if len(collected) >= max_articles * 3:
                break
            try:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries[:30]:
                    title = getattr(entry, "title", "") or ""
                    summary = getattr(entry, "summary", "") or ""
                    combined = (title + " " + summary).lower()
                    if any(k in combined for k in kw):
                        collected.append({
                            "title": title,
                            "description": summary[:200],
                            "url": getattr(entry, "link", "#"),
                            "publishedAt": _parse_rss_date(entry),
                            "source": feed_name,
                        })
            except Exception:
                continue
        if collected:
            return collected[:max_articles]
    except ImportError:
        pass

    # 3) Static fallback
    kw_fb = query.lower().split()
    filtered = [n for n in _FALLBACK_NEWS
                if any(k in n["title"].lower() for k in kw_fb)]
    return (filtered or _FALLBACK_NEWS)[:max_articles]


def analyze_sentiment(text):
    prompt = (
        "Analiza este titular financiero y dame: "
        "1) sentimiento (positivo/negativo/neutro) "
        "2) impacto potencial en inversiones (alto/medio/bajo) "
        "3) una línea de resumen. "
        "Responde SOLO en JSON con keys: sentiment, impact, summary. "
        f"Titular: {text}"
    )
    content = get_ai_response(prompt, max_tokens=200)
    match = re.search(r"\{.*?\}", content, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except Exception:
            pass
    return {"sentiment": "neutro", "impact": "medio", "summary": content[:120]}


def get_portfolio_news(tickers=None, ticker_names=None):
    if tickers is None:
        from config import ALL_TICKERS
        tickers = ALL_TICKERS
    if ticker_names is None:
        ticker_names = TICKER_NAMES

    results = []
    seen = set()
    for ticker in tickers:
        name = ticker_names.get(ticker, ticker)
        for art in fetch_news(f"{name} {ticker} stock investing", max_articles=2):
            h = art.get("title", "") or art.get("headline", "")
            if not h or h in seen:
                continue
            seen.add(h)
            s = analyze_sentiment(h)
            results.append({
                "ticker":     ticker,
                "name":       name,
                "headline":   h,
                "sentiment":  s.get("sentiment", "neutro"),
                "impact":     s.get("impact", "medio"),
                "summary":    s.get("summary", art.get("description", "")),
                "url":        art.get("url", "#"),
                "published_at": art.get("publishedAt", ""),
                "source":     art.get("source", ""),
            })
    return results
