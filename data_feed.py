"""
Ambil data candle XAUUSD lewat TickerAll - 1 timeframe (M5) untuk strategi RSI.
"""
import pandas as pd

from config import SYMBOL, TIMEFRAME

_HOURS_LOOKBACK = {
    "M1": 6, "M5": 26, "M15": 76, "H1": 500, "H4": 2000, "D1": 7200,
}


def get_candles(client, account_id: str, limit: int = 300) -> pd.DataFrame:
    hours = _HOURS_LOOKBACK.get(TIMEFRAME, 26)
    try:
        bars = client.candles.get(account_id, symbol=SYMBOL, hours=hours, timeframe=TIMEFRAME)
    except Exception as e:
        print(f"Error ambil candle {TIMEFRAME} untuk symbol '{SYMBOL}': {e}")
        return pd.DataFrame()

    if not bars:
        return pd.DataFrame()

    data = [{
        "time": c.timestamp, "open": c.open, "high": c.high,
        "low": c.low, "close": c.close, "volume": getattr(c, "volume", 0),
    } for c in bars]

    df = pd.DataFrame(data)
    df["time"] = pd.to_datetime(df["time"])
    df = df.sort_values("time").reset_index(drop=True)
    return df.tail(limit)
