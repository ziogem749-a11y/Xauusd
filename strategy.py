"""
Strategi: RSI Reversal - sederhana, sinyal lebih sering.
RSI dihitung pakai metode Wilder's Smoothing (sama seperti MT5/TradingView),
supaya angka RSI yang dibaca bot konsisten dengan yang terlihat di chart MT5.

Logic:
- RSI < RSI_OVERSOLD  -> BUY (harga dianggap sudah terlalu murah sesaat)
- RSI > RSI_OVERBOUGHT -> SELL (harga dianggap sudah terlalu mahal sesaat)
- SL = 1x ATR, TP = RISK_REWARD_RATIO x jarak SL (disiplin, RR ketat)
"""
import pandas as pd

from config import RSI_PERIOD, RSI_OVERBOUGHT, RSI_OVERSOLD, ATR_PERIOD, RISK_REWARD_RATIO, ATR_SL_MULTIPLIER


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    delta = df["close"].diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)

    avg_gain = gain.ewm(alpha=1 / RSI_PERIOD, adjust=False, min_periods=RSI_PERIOD).mean()
    avg_loss = loss.ewm(alpha=1 / RSI_PERIOD, adjust=False, min_periods=RSI_PERIOD).mean()

    rs = avg_gain / avg_loss.replace(0, pd.NA)
    df["rsi"] = 100 - (100 / (1 + rs))

    high_low = df["high"] - df["low"]
    high_close = (df["high"] - df["close"].shift()).abs()
    low_close = (df["low"] - df["close"].shift()).abs()
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    df["atr"] = tr.ewm(alpha=1 / ATR_PERIOD, adjust=False, min_periods=ATR_PERIOD).mean()

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
