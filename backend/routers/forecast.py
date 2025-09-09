from fastapi import APIRouter
from services.prices import fetch_prices
from services.forecast import train_and_predict
import numpy as np
import pandas as pd
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("")
def get_forecast(symbol: str, horizon: int = 30):
    try:
        df = fetch_prices(symbol, period="5y", interval="1d")
        if df.empty:
            return {"symbol": symbol.upper(), "horizon": horizon, "forecast": [], "error": "No data for symbol"}
        fcst = train_and_predict(df, horizon_days=horizon)
        out = [
            {"date": str(r["ds"]), "yhat": float(r["yhat"]),
             "lower": float(r["yhat_lower"]), "upper": float(r["yhat_upper"])}
            for _, r in fcst.iterrows()
        ]
        return {"symbol": symbol.upper(), "horizon": horizon, "forecast": out}
    except Exception as e:
        # Log the prophet error and provide a simple linear fallback so the UI still works
        logger.exception("forecast failed: %s", e)
        try:
            last30 = df["close"].tail(30).to_numpy()
            if last30.size >= 2:
                x = np.arange(last30.size)
                m, b = np.polyfit(x, last30, 1)  # slope, intercept
                last_date = pd.to_datetime(df["date"]).max()
                future = []
                for i in range(1, horizon + 1):
                    d = (last_date + pd.Timedelta(days=i)).date().isoformat()
                    yhat = float(m * (last30.size + i) + b)
                    future.append({
                        "date": d,
                        "yhat": yhat,
                        "lower": yhat * 0.98,
                        "upper": yhat * 1.02
                    })
                return {"symbol": symbol.upper(), "horizon": horizon, "forecast": future,
                        "note": "fallback linear forecast", "error": str(e)}
        except Exception as e2:
            logger.exception("fallback forecast failed: %s", e2)

        # If even fallback fails, return an empty forecast (no crash)
        return {"symbol": symbol.upper(), "horizon": horizon, "forecast": [], "error": str(e)}
