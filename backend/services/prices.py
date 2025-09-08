import yfinance as yf
import pandas as pd

def fetch_prices(symbol: str, period="5y", interval="1d") -> pd.DataFrame:
    df = yf.download(symbol, period=period, interval=interval, auto_adjust=True, progress=False)
    return df.reset_index().rename(columns=str.lower)  # columns like: date, close, ...
