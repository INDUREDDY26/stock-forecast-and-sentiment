from fastapi import APIRouter, HTTPException
from services.prices import fetch_prices

router = APIRouter()


@router.get("")
def get_prices(symbol: str, period: str = "5y", interval: str = "1d"):
    try:
        df = fetch_prices(symbol, period, interval)
        if df.empty:
            raise HTTPException(status_code=404, detail="No data for symbol")
        return {
            "symbol": symbol.upper(),
            "data": [
                {"date": str(r["date"]), "close": float(r["close"])}
                for _, r in df.iterrows()
            ],
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
