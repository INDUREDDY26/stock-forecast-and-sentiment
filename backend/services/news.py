import requests
from xml.etree import ElementTree as ET
from urllib.parse import quote_plus
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
      "AppleWebKit/605.1.15 (KHTML, like Gecko) "
      "Version/17.0 Safari/605.1.15")

def _parse_rss(content: bytes, limit: int):
    root = ET.fromstring(content)
    items = root.findall(".//item")[:limit]
    out = []
    for it in items:
        title = (it.findtext("title") or "").strip()
        link  = (it.findtext("link") or "").strip()
        pub   = (it.findtext("{http://purl.org/dc/elements/1.1/}date") or it.findtext("pubDate") or "").strip()
        if not title:
            continue
        score = analyzer.polarity_scores(title)["compound"]
        label = "positive" if score > 0.2 else "negative" if score < -0.2 else "neutral"
        out.append({"title": title, "url": link, "published_at": pub, "score": score, "label": label})
    return out

def fetch_news(symbol: str, limit: int = 10):
    headers = {"User-Agent": UA, "Accept": "application/rss+xml,application/xml;q=0.9,*/*;q=0.8"}

    # 1) Try Yahoo Finance RSS
    yahoo = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={symbol}&region=US&lang=en-US"
    try:
        r = requests.get(yahoo, headers=headers, timeout=10)
        if r.ok and b"<rss" in r.content[:200].lower():
            data = _parse_rss(r.content, limit)
            if data:
                return data
    except Exception:
        pass  # fall through

    # 2) Fallback: Google News RSS for "<SYMBOL> stock"
    q = quote_plus(f"{symbol} stock")
    gnews = f"https://news.google.com/rss/search?q={q}&hl=en-US&gl=US&ceid=US:en"
    try:
        r = requests.get(gnews, headers=headers, timeout=10)
        if r.ok and b"<rss" in r.content[:200].lower():
            return _parse_rss(r.content, limit)
    except Exception:
        pass

    # 3) Nothing found
    return []
