"""
Ambil data candle XAUUSD lewat TickerAll (broker session ke HFM).
Butuh: pip install tickerall pandas
"""
import pandas as pd

from config import SYMBOL, TIMEFRAME

_TIMEFRAME_TO_HOURS_FOR_300_BARS = {
    "M1": 6, "M5": 26, "M15": 76, "H1": 300, "D1": 7200,
}


def get_candles(client, account_id: str, limit: int = 300) -> pd.DataFrame:
    hours = _TIMEFRAME_TO_HOURS_FOR_300_BARS.get(TIMEFRAME, 76)

    bars = client.candles.get(account_id, symbol=SYMBOL, hours=hours, timeframe=TIMEFRAME)

    if not bars:
        return pd.DataFrame()

    data = [{
        "time": c.timestamp,
        "open": c.open,
        "high": c.high,
        "low": c.low,
        "close": c.close,
        "volume": getattr(c, "volume", 0),
    } for c in bars]

    df = pd.DataFrame(data)
    df["time"] = pd.to_datetime(df["time"])
    df = df.sort_values("time").reset_index(drop=True)
    return df.tail(limit)
