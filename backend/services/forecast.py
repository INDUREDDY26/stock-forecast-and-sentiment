import pandas as pd
from prophet import Prophet

def train_and_predict(df_prices: pd.DataFrame, horizon_days: int = 30):
    df = df_prices.loc[:, ["date","close"]].copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    try: df["date"] = df["date"].dt.tz_localize(None)
    except Exception: pass

    # ensure "close" is a 1-D numeric Series
    if isinstance(df["close"], pd.DataFrame):
        df["close"] = df["close"].iloc[:, 0]
    df["close"] = pd.to_numeric(df["close"], errors="coerce")

    df = df.dropna(subset=["date","close"]).sort_values("date")
    df = df.rename(columns={"date":"ds","close":"y"})

    if len(df) < 50:
        raise ValueError(f"Not enough rows to forecast (have {len(df)}).")

    m = Prophet(daily_seasonality=True)
    m.fit(df)
    future = m.make_future_dataframe(periods=horizon_days, freq="D")
    fcst = m.predict(future)[["ds","yhat","yhat_lower","yhat_upper"]]
    return fcst.tail(horizon_days)
