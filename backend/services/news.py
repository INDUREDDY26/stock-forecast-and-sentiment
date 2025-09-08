import requests
from xml.etree import ElementTree as ET
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()


def fetch_news(symbol: str, limit: int = 10):
    url = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={symbol}&region=US&lang=en-US"
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    root = ET.fromstring(r.content)
    items = root.findall(".//item")[:limit]
    out = []
    for it in items:
        title = (it.findtext("title") or "").strip()
        link = (it.findtext("link") or "").strip()
        pub = (
            it.findtext("{http://purl.org/dc/elements/1.1/}date")
            or it.findtext("pubDate")
            or ""
        ).strip()
        score = analyzer.polarity_scores(title)["compound"]
        label = "positive" if score > 0.2 else "negative" if score < -0.2 else "neutral"
        out.append(
            {
                "title": title,
                "url": link,
                "published_at": pub,
                "score": score,
                "label": label,
            }
        )
    return out
