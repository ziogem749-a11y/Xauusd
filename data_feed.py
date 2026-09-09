"""
Ambil data candle XAUUSD lewat TickerAll (broker session ke HFM).
Butuh: pip install tickerall pandas
"""
import pandas as pd

from config import SYMBOL, TIMEFRAME

_TIMEFRAME_TO_HOURS_FOR_300_BARS = {
    "M1": 6, "M5": 26, "M15": 76, "H1": 300, "D1": 7200,
}

_printed_symbols_debug = False


def get_candles(client, account_id: str, limit: int = 300) -> pd.DataFrame:
    global _printed_symbols_debug
    hours = _TIMEFRAME_TO_HOURS_FOR_300_BARS.get(TIMEFRAME, 76)

    try:
        bars = client.candles.get(account_id, symbol=SYMBOL, hours=hours, timeframe=TIMEFRAME)
    except Exception as e:
        print(f"Error ambil candle untuk symbol '{SYMBOL}': {e}")
        bars = None

    if not bars:
        if not _printed_symbols_debug:
            try:
                symbols = client.accounts.symbols(account_id)
                gold_like = [s for s in symbols if "XAU" in str(s).upper() or "GOLD" in str(s).upper()]
                print(f"DEBUG: symbol '{SYMBOL}' gak ketemu/kosong datanya.")
                print(f"DEBUG: symbol yang mengandung XAU/GOLD di akun ini: {gold_like}")
            except Exception as e:
                print(f"DEBUG: gagal ambil daftar symbols: {e}")
            _printed_symbols_debug = True
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
