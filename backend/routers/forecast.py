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
        # 1) get clean price data
        df = fetch_prices(symbol, period="5y", interval="1d")
        if df.empty:
            return {"symbol": symbol.upper(), "horizon": horizon, "engine": "none", "forecast": [], "error": "No data"}
        # 2) try prophet
        try:
            fcst = train_and_predict(df, horizon_days=horizon)
            out = [
                {"date": str(r["ds"]), "yhat": float(r["yhat"]),
                 "lower": float(r["yhat_lower"]), "upper": float(r["yhat_upper"])}
                for _, r in fcst.iterrows()
            ]
            return {"symbol": symbol.upper(), "horizon": horizon, "engine": "prophet", "forecast": out}
        except Exception as e:
            logger.exception("prophet failed: %s", e)
            # 3) linear fallback so UI still works
            try:
                last = df["close"].astype(float).tail(30).to_numpy()
                if last.size >= 2:
                    x = np.arange(last.size)
                    m, b = np.polyfit(x, last, 1)
                    last_date = pd.to_datetime(df["date"]).max()
                    future = []
                    for i in range(1, horizon + 1):
                        d = (last_date + pd.Timedelta(days=i)).date().isoformat()
                        yhat = float(m * (last.size + i) + b)
                        future.append({"date": d, "yhat": yhat, "lower": yhat * 0.98, "upper": yhat * 1.02})
                    return {"symbol": symbol.upper(), "horizon": horizon, "engine": "fallback",
                            "forecast": future, "error": str(e)}
                # not enough data for fallback
                return {"symbol": symbol.upper(), "horizon": horizon, "engine": "fallback",
                        "forecast": [], "error": f"{e} (and not enough data for fallback)"}
            except Exception as e2:
                logger.exception("fallback failed: %s", e2)
                return {"symbol": symbol.upper(), "horizon": horizon, "engine": "error",
                        "forecast": [], "error": f"{e} | fallback error: {e2}"}
    except Exception as outer:
        logger.exception("outer error in /forecast: %s", outer)
        return {"symbol": symbol.upper(), "horizon": horizon, "engine": "error",
                "forecast": [], "error": str(outer)}
