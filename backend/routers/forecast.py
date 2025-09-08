from fastapi import APIRouter, HTTPException
from services.prices import fetch_prices
from services.forecast import train_and_predict

router = APIRouter()


@router.get("")
def get_forecast(symbol: str, horizon: int = 30):
    try:
        df = fetch_prices(symbol, period="5y", interval="1d")
        if df.empty:
            raise HTTPException(status_code=404, detail="No data for symbol")
        fcst = train_and_predict(df, horizon_days=horizon)
        return {
            "symbol": symbol.upper(),
            "horizon": horizon,
            "forecast": [
                {
                    "date": str(r["ds"]),
                    "yhat": float(r["yhat"]),
                    "lower": float(r["yhat_lower"]),
                    "upper": float(r["yhat_upper"]),
                }
                for _, r in fcst.iterrows()
            ],
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
