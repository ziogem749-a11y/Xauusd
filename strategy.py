"""
Strategi: RSI Reversal (M5) - sederhana, sinyal lebih sering.
"""
import pandas as pd

from config import RSI_PERIOD, RSI_OVERBOUGHT, RSI_OVERSOLD, ATR_PERIOD, RISK_REWARD_RATIO, ATR_SL_MULTIPLIER


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    delta = df["close"].diff()
    gain = delta.where(delta > 0, 0).rolling(RSI_PERIOD).mean()
    loss = -delta.where(delta < 0, 0).rolling(RSI_PERIOD).mean()
    rs = gain / loss.replace(0, pd.NA)
    df["rsi"] = 100 - (100 / (1 + rs))

    high_low = df["high"] - df["low"]
    high_close = (df["high"] - df["close"].shift()).abs()
    low_close = (df["low"] - df["close"].shift()).abs()
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    df["atr"] = tr.rolling(ATR_PERIOD).mean()

    return df


def check_signal(df: pd.DataFrame) -> dict:
    df = add_indicators(df)
    min_bars = max(RSI_PERIOD, ATR_PERIOD) + 2
    if len(df) < min_bars:
        return {"signal": None, "reason": "data belum cukup"}

    curr = df.iloc[-1]

    if pd.isna(curr["rsi"]) or pd.isna(curr["atr"]) or curr["atr"] <= 0:
        return {"signal": None, "reason": "indikator belum siap"}

    if curr["rsi"] < RSI_OVERSOLD:
        entry = curr["close"]
        sl = entry - curr["atr"] * ATR_SL_MULTIPLIER
        tp = entry + (entry - sl) * RISK_REWARD_RATIO
        return {
            "signal": "BUY", "entry": entry, "sl": sl, "tp": tp,
            "reason": f"RSI oversold ({curr['rsi']:.1f} < {RSI_OVERSOLD})",
        }

    if curr["rsi"] > RSI_OVERBOUGHT:
        entry = curr["close"]
        sl = entry + curr["atr"] * ATR_SL_MULTIPLIER
        tp = entry - (sl - entry) * RISK_REWARD_RATIO
        return {
            "signal": "SELL", "entry": entry, "sl": sl, "tp": tp,
            "reason": f"RSI overbought ({curr['rsi']:.1f} > {RSI_OVERBOUGHT})",
        }

    return {"signal": None, "reason": f"RSI netral ({curr['rsi']:.1f})"}
