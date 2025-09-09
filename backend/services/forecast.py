import pandas as pd
from prophet import Prophet

def train_and_predict(df_prices: pd.DataFrame, horizon_days: int = 30):
    # Keep only the columns we need and make a copy
    df = df_prices.loc[:, ["date", "close"]].copy()

    # Prophet expects: ds (datetime), y (float)
    df = df.rename(columns={"date": "ds", "close": "y"})
    df["ds"] = pd.to_datetime(df["ds"], errors="coerce")
    df["y"]  = pd.to_numeric(df["y"], errors="coerce")

    # Drop bad rows and sort
    df = df.dropna(subset=["ds", "y"]).sort_values("ds")

    # Ensure we have enough rows to model
    if len(df) < 20:
        raise ValueError(f"Not enough rows to forecast (have {len(df)}).")

    # Fit and predict
    m = Prophet(daily_seasonality=True)
    m.fit(df)
    future = m.make_future_dataframe(periods=horizon_days)
    fcst = m.predict(future)[["ds", "yhat", "yhat_lower", "yhat_upper"]]
    return fcst.tail(horizon_days)
