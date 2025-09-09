import yfinance as yf
import pandas as pd

def fetch_prices(symbol: str, period="5y", interval="1d") -> pd.DataFrame:
    # 1) Try primary endpoint
    df = yf.download(
        symbol,
        period=period,
        interval=interval,
        auto_adjust=True,
        progress=False,
        threads=False,      # more deterministic
        group_by="column"   # try to avoid multiindex, but flatten anyway if present
    )

    # 2) Fallback to history() if empty
    if df is None or len(df) == 0:
        df = yf.Ticker(symbol).history(
            period=period,
            interval=interval,
            auto_adjust=True
        )

    # 3) If still empty -> canonical empty frame
    if df is None or len(df) == 0:
        return pd.DataFrame(columns=["date", "close"])

    # --- FLATTEN COLUMNS IF MULTIINDEX ---
    if isinstance(df.columns, pd.MultiIndex):
        # If one level is 'Ticker'/'Symbol', select this symbol across that level
        level_names = [ (n or "").lower() for n in df.columns.names ]
        if "ticker" in level_names or "symbol" in level_names:
            lvl = level_names.index("ticker") if "ticker" in level_names else level_names.index("symbol")
            try:
                # pick this ticker across that level
                if symbol in df.columns.get_level_values(lvl):
                    df = df.xs(symbol, level=lvl, axis=1)
                else:
                    # single-ticker case, just drop last level
                    df = df.droplevel(-1, axis=1)
            except Exception:
                # generic flatten: drop levels until single index remains
                while isinstance(df.columns, pd.MultiIndex) and df.columns.nlevels > 1:
                    df = df.droplevel(-1, axis=1)
        else:
            # generic flatten
            while isinstance(df.columns, pd.MultiIndex) and df.columns.nlevels > 1:
                df = df.droplevel(-1, axis=1)

    # 4) Make 'Date' a column
    df = df.reset_index()

    # 5) Standardize names
    rename_map = {
        "Date": "date", "Datetime": "date", "date": "date",
        "Close": "close", "Adj Close": "adj_close", "Adj close": "adj_close",
        "close": "close", "adj close": "adj_close", "Adj_Close": "adj_close"
    }
    df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})
    df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]
    df = df.loc[:, ~df.columns.duplicated()]

    # 6) Prefer 'close'; fallback to 'adj_close'
    if "close" not in df.columns and "adj_close" in df.columns:
        df["close"] = df["adj_close"]

    # 7) Build canonical output
    if not {"date", "close"}.issubset(df.columns):
        return pd.DataFrame(columns=["date", "close"])

    out = df[["date", "close"]].copy()
    out["date"] = pd.to_datetime(out["date"], errors="coerce")
    try:
        out["date"] = out["date"].dt.tz_localize(None)
    except Exception:
        pass

    # In rare cases 'close' can still be a DataFrame (duplicate-named columns)
    if "close" in out.columns and isinstance(out["close"], pd.DataFrame):
        out["close"] = out["close"].iloc[:, 0]

    out["close"] = pd.to_numeric(out["close"], errors="coerce")
    out = out.dropna(subset=["date", "close"]).sort_values("date")
    return out.reindex(columns=["date", "close"])
