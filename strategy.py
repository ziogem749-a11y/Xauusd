"""
Logic strategi: EMA Trend Filter + Asia Session Breakout + ATR untuk SL/TP.
Butuh: pip install pandas numpy
"""
import pandas as pd
import numpy as np

from config import (
    EMA_FAST, EMA_SLOW, ATR_PERIOD,
    ATR_SL_MULTIPLIER, ATR_TP_MULTIPLIER,
    ASIA_SESSION_START_HOUR_WIB, ASIA_SESSION_END_HOUR_WIB,
)


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Tambah kolom EMA fast/slow dan ATR ke DataFrame candle."""
    df = df.copy()
    df["ema_fast"] = df["close"].ewm(span=EMA_FAST, adjust=False).mean()
    df["ema_slow"] = df["close"].ewm(span=EMA_SLOW, adjust=False).mean()

    high_low = df["high"] - df["low"]
    high_close = (df["high"] - df["close"].shift()).abs()
    low_close = (df["low"] - df["close"].shift()).abs()
    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    df["atr"] = true_range.rolling(ATR_PERIOD).mean()

    return df


def get_asia_session_range(df: pd.DataFrame) -> tuple:
    """
    Ambil high/low dari candle-candle yang jatuh di jam sesi Asia (WIB) hari ini.
    Asumsi df["time"] sudah dalam UTC — konversi ke WIB (UTC+7) dulu.
    """
    df = df.copy()
    df["time_wib"] = df["time"] + pd.Timedelta(hours=7)
    today_wib = df["time_wib"].iloc[-1].date()

    mask = (
        (df["time_wib"].dt.date == today_wib) &
        (df["time_wib"].dt.hour >= ASIA_SESSION_START_HOUR_WIB) &
        (df["time_wib"].dt.hour < ASIA_SESSION_END_HOUR_WIB)
    )
    asia_candles = df[mask]

    if asia_candles.empty:
        return None, None

    return asia_candles["high"].max(), asia_candles["low"].min()


def check_signal(df: pd.DataFrame) -> dict:
    """
    Cek apakah candle terakhir memenuhi syarat entry.
    Return dict: {"signal": "BUY"/"SELL"/None, "entry": float, "sl": float, "tp": float, "atr": float}
    """
    df = add_indicators(df)
    if len(df) < max(EMA_SLOW, ATR_PERIOD) + 1:
        return {"signal": None}

    last = df.iloc[-1]
    asia_high, asia_low = get_asia_session_range(df)

    if asia_high is None or pd.isna(last["atr"]):
        return {"signal": None}

    uptrend = last["ema_fast"] > last["ema_slow"]
    downtrend = last["ema_fast"] < last["ema_slow"]

    breakout_up = last["close"] > asia_high
    breakout_down = last["close"] < asia_low

    if uptrend and breakout_up:
        entry = last["close"]
        sl = entry - (last["atr"] * ATR_SL_MULTIPLIER)
        tp = entry + (last["atr"] * ATR_TP_MULTIPLIER)
        return {"signal": "BUY", "entry": entry, "sl": sl, "tp": tp, "atr": last["atr"]}

    if downtrend and breakout_down:
        entry = last["close"]
        sl = entry + (last["atr"] * ATR_SL_MULTIPLIER)
        tp = entry - (last["atr"] * ATR_TP_MULTIPLIER)
        return {"signal": "SELL", "entry": entry, "sl": sl, "tp": tp, "atr": last["atr"]}

    return {"signal": None}
