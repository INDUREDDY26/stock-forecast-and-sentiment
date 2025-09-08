import pandas as pd
from prophet import Prophet

def train_and_predict(df_prices: pd.DataFrame, horizon_days: int = 30):
    # Prophet expects columns ds (date) and y (value)
    df = df_prices[["date", "close"]].rename(columns={"date": "ds", "close": "y"})
    m = Prophet(daily_seasonality=True)
    m.fit(df)
    future = m.make_future_dataframe(periods=horizon_days)
    fcst = m.predict(future)[["ds", "yhat", "yhat_lower", "yhat_upper"]]
    return fcst.tail(horizon_days)
