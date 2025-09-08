from fastapi import APIRouter, HTTPException
from services.news import fetch_news

router = APIRouter()


@router.get("")
def get_news(symbol: str, limit: int = 10):
    try:
        data = fetch_news(symbol, limit)
        return {"symbol": symbol.upper(), "news": data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
