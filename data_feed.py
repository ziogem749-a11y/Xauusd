"""
Ambil data candle XAUUSD lewat TickerAll - butuh 2 timeframe (H1 buat tren, M15 buat entry).
"""
import pandas as pd

from config import SYMBOL, TIMEFRAME_TREND, TIMEFRAME_ENTRY

_HOURS_LOOKBACK = {
    "M1": 6, "M5": 26, "M15": 76, "H1": 500, "H4": 2000, "D1": 7200,
}


def _fetch(client, account_id: str, timeframe: str, limit: int) -> pd.DataFrame:
    hours = _HOURS_LOOKBACK.get(timeframe, 300)
    try:
        bars = client.candles.get(account_id, symbol=SYMBOL, hours=hours, timeframe=timeframe)
    except Exception as e:
        print(f"Error ambil candle {timeframe} untuk symbol '{SYMBOL}': {e}")
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


def get_htf_candles(client, account_id: str, limit: int = 300) -> pd.DataFrame:
    return _fetch(client, account_id, TIMEFRAME_TREND, limit)


def get_ltf_candles(client, account_id: str, limit: int = 300) -> pd.DataFrame:
    return _fetch(client, account_id, TIMEFRAME_ENTRY, limit)
