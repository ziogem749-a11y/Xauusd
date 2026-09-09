"""
Strategi: EMA Crossover - sederhana dan stabil.
EMA cepat (9) motong ke atas EMA lambat (21) -> BUY
EMA cepat (9) motong ke bawah EMA lambat (21) -> SELL
SL = 1x ATR, TP = RISK_REWARD_RATIO x jarak SL.
"""
import pandas as pd

from config import EMA_FAST, EMA_SLOW, ATR_PERIOD, ATR_SL_MULTIPLIER, RISK_REWARD_RATIO


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["ema_fast"] = df["close"].ewm(span=EMA_FAST, adjust=False).mean()
    df["ema_slow"] = df["close"].ewm(span=EMA_SLOW, adjust=False).mean()

    high_low = df["high"] - df["low"]
    high_close = (df["high"] - df["close"].shift()).abs()
    low_close = (df["low"] - df["close"].shift()).abs()
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    df["atr"] = tr.ewm(alpha=1 / ATR_PERIOD, adjust=False, min_periods=ATR_PERIOD).mean()

    return df


def check_signal(df: pd.DataFrame) -> dict:
    df = add_indicators(df)
    min_bars = max(EMA_SLOW, ATR_PERIOD) + 2
    if len(df) < min_bars:
        return {"signal": None, "reason": "data belum cukup"}

    curr = df.iloc[-1]
    prev = df.iloc[-2]

    if pd.isna(curr["atr"]) or curr["atr"] <= 0:
        return {"signal": None, "reason": "ATR belum siap"}

    crossed_up = prev["ema_fast"] <= prev["ema_slow"] and curr["ema_fast"] > curr["ema_slow"]
    crossed_down = prev["ema_fast"] >= prev["ema_slow"] and curr["ema_fast"] < curr["ema_slow"]

    if crossed_up:
        entry = curr["close"]
        sl = entry - curr["atr"] * ATR_SL_MULTIPLIER
        tp = entry + (entry - sl) * RISK_REWARD_RATIO
        return {
            "signal": "BUY", "entry": entry, "sl": sl, "tp": tp,
            "reason": f"EMA{EMA_FAST} cross up EMA{EMA_SLOW}",
        }

    if crossed_down:
        entry = curr["close"]
        sl = entry + curr["atr"] * ATR_SL_MULTIPLIER
        tp = entry - (sl - entry) * RISK_REWARD_RATIO
        return {
            "signal": "SELL", "entry": entry, "sl": sl, "tp": tp,
            "reason": f"EMA{EMA_FAST} cross down EMA{EMA_SLOW}",
        }

    return {"signal": None, "reason": f"belum ada crossover (fast={curr['ema_fast']:.2f}, slow={curr['ema_slow']:.2f})"}
