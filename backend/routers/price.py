from fastapi import APIRouter, HTTPException
from services.prices import fetch_prices

router = APIRouter()

@router.get("")
def get_prices(symbol: str, period: str = "5y", interval: str = "1d"):
    df = fetch_prices(symbol, period, interval)
    if df.empty:
        raise HTTPException(status_code=404, detail="No data for symbol")
    data = (
        df.assign(date=df["date"].dt.date.astype(str), close=df["close"].astype(float))
          [["date","close"]]
          .to_dict(orient="records")
    )
    return {"symbol": symbol.upper(), "data": data}
