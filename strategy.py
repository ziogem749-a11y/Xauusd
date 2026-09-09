"""
Strategi: Random Signal - setiap kali dicek dan tidak ada posisi terbuka,
bot akan random pilih BUY atau SELL. Tidak ada dasar analisa teknikal sama
sekali - dipakai supaya bot selalu aktif trading tanpa menunggu kondisi
tertentu terpenuhi.
SL = 1x ATR, TP = RISK_REWARD_RATIO x jarak SL (RR tetap disiplin walau
arah entry-nya acak).
"""
import random
import pandas as pd

from config import ATR_PERIOD, ATR_SL_MULTIPLIER, RISK_REWARD_RATIO


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    high_low = df["high"] - df["low"]
    high_close = (df["high"] - df["close"].shift()).abs()
    low_close = (df["low"] - df["close"].shift()).abs()
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    df["atr"] = tr.ewm(alpha=1 / ATR_PERIOD, adjust=False, min_periods=ATR_PERIOD).mean()
    return df


def check_signal(df: pd.DataFrame) -> dict:
    df = add_indicators(df)
    min_bars = ATR_PERIOD + 2
    if len(df) < min_bars:
        return {"signal": None, "reason": "data belum cukup"}

    curr = df.iloc[-1]

    if pd.isna(curr["atr"]) or curr["atr"] <= 0:
        return {"signal": None, "reason": "ATR belum siap"}

    side = random.choice(["BUY", "SELL"])
    entry = curr["close"]

    if side == "BUY":
        sl = entry - curr["atr"] * ATR_SL_MULTIPLIER
        tp = entry + (entry - sl) * RISK_REWARD_RATIO
    else:
        sl = entry + curr["atr"] * ATR_SL_MULTIPLIER
        tp = entry - (sl - entry) * RISK_REWARD_RATIO

    return {
        "signal": side, "entry": entry, "sl": sl, "tp": tp,
        "reason": "Random signal (tanpa analisa teknikal)",
    }
