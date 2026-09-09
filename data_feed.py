"""
Ambil data candle XAUUSD lewat TickerAll - 1 timeframe (M1/M5/dst) untuk strategi RSI.
"""
import datetime
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
    df["time"] = pd.to_datetime(df["time"], unit="s")
    df = df.sort_values("time").reset_index(drop=True)
    return df.tail(limit)


def append_live_candle(df: pd.DataFrame, live_price) -> pd.DataFrame:
    """
    Tambahkan 1 baris "candle hidup" pakai harga live sekarang, supaya indikator
    (RSI/ATR) dihitung sampai ke tick terakhir - meniru cara MT5/TradingView
    menghitung indikator di candle yang masih berjalan (belum closed).
    """
    if df.empty or live_price is None:
        return df

    last_close = df["close"].iloc[-1]
    new_row = {
        "time": datetime.datetime.utcnow(),
        "open": last_close,
        "high": max(last_close, live_price),
        "low": min(last_close, live_price),
        "close": live_price,
        "volume": 0,
    }
    return pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
