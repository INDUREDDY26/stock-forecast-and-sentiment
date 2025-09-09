from fastapi import APIRouter
from services.news import fetch_news

router = APIRouter()


@router.get("")
def get_news(symbol: str, limit: int = 10):
    try:
        data = fetch_news(symbol, limit)
    except Exception:
        data = []  # On any error, return empty list instead of failing the request.
    return {"symbol": symbol.upper(), "news": data}
