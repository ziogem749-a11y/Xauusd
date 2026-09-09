"""
Strategi: Trend Pullback Entry.

1. Tren besar ditentukan dari H1 (EMA50 vs EMA200).
2. Entry dicari di M15, nunggu harga PULLBACK ke EMA21.
3. Konfirmasi pola candle (bullish/bearish engulfing) di area pullback.
4. Filter RSI - hindari entry saat RSI masih ekstrem searah posisi.
5. SL dari struktur (swing low/high N candle terakhir).
6. TP dari rasio Risk:Reward.
"""
import pandas as pd
import numpy as np

from config import (
    EMA_TREND_FAST, EMA_TREND_SLOW, EMA_PULLBACK,
    RSI_PERIOD, RSI_OVERBOUGHT, RSI_OVERSOLD,
    SWING_LOOKBACK, RISK_REWARD_RATIO,
    PULLBACK_TOLERANCE_ATR, ATR_PERIOD,
)


def add_indicators_htf(df_h1: pd.DataFrame) -> pd.DataFrame:
    df = df_h1.copy()
    df["ema_trend_fast"] = df["close"].ewm(span=EMA_TREND_FAST, adjust=False).mean()
    df["ema_trend_slow"] = df["close"].ewm(span=EMA_TREND_SLOW, adjust=False).mean()
    return df


def add_indicators_ltf(df_m15: pd.DataFrame) -> pd.DataFrame:
    df = df_m15.copy()
    df["ema_pullback"] = df["close"].ewm(span=EMA_PULLBACK, adjust=False).mean()

    delta = df["close"].diff()
    gain = delta.where(delta > 0, 0).rolling(RSI_PERIOD).mean()
    loss = -delta.where(delta < 0, 0).rolling(RSI_PERIOD).mean()
    rs = gain / loss.replace(0, np.nan)
    df["rsi"] = 100 - (100 / (1 + rs))

    high_low = df["high"] - df["low"]
    high_close = (df["high"] - df["close"].shift()).abs()
    low_close = (df["low"] - df["close"].shift()).abs()
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    df["atr"] = tr.rolling(ATR_PERIOD).mean()

    return df


def get_trend(df_h1_with_indicators: pd.DataFrame) -> str:
    last = df_h1_with_indicators.iloc[-1]
    if pd.isna(last["ema_trend_fast"]) or pd.isna(last["ema_trend_slow"]):
        return "FLAT"
    if last["ema_trend_fast"] > last["ema_trend_slow"]:
        return "UP"
    elif last["ema_trend_fast"] < last["ema_trend_slow"]:
        return "DOWN"
    return "FLAT"


def _is_bullish_engulfing(prev, curr) -> bool:
    return (prev["close"] < prev["open"]) and (curr["close"] > curr["open"]) and \
           (curr["close"] >= prev["open"]) and (curr["open"] <= prev["close"])


def _is_bearish_engulfing(prev, curr) -> bool:
    return (prev["close"] > prev["open"]) and (curr["close"] < curr["open"]) and \
           (curr["close"] <= prev["open"]) and (curr["open"] >= prev["close"])


def check_signal(df_h1: pd.DataFrame, df_m15: pd.DataFrame) -> dict:
    df_h1i = add_indicators_htf(df_h1)
    df_m15i = add_indicators_ltf(df_m15)

    min_bars_h1 = max(EMA_TREND_FAST, EMA_TREND_SLOW) + 1
    min_bars_m15 = max(EMA_PULLBACK, RSI_PERIOD, ATR_PERIOD, SWING_LOOKBACK) + 2
    if len(df_h1i) < min_bars_h1 or len(df_m15i) < min_bars_m15:
        return {"signal": None, "reason": "data belum cukup"}

    trend = get_trend(df_h1i)
    if trend == "FLAT":
        return {"signal": None, "reason": "tren H1 gak jelas"}

    curr = df_m15i.iloc[-1]
    prev = df_m15i.iloc[-2]

    if pd.isna(curr["atr"]) or pd.isna(curr["ema_pullback"]) or pd.isna(curr["rsi"]):
        return {"signal": None, "reason": "indikator M15 belum lengkap"}

    distance_to_ema = abs(curr["close"] - curr["ema_pullback"])
    near_pullback_zone = distance_to_ema <= (curr["atr"] * PULLBACK_TOLERANCE_ATR)

    if not near_pullback_zone:
        return {"signal": None, "reason": "harga belum di area pullback"}

    swing_window = df_m15i.iloc[-(SWING_LOOKBACK + 1):-1]

    if trend == "UP":
        confirmed = _is_bullish_engulfing(prev, curr)
        rsi_ok = curr["rsi"] < RSI_OVERBOUGHT
        if confirmed and rsi_ok:
            entry = curr["close"]
            sl = swing_window["low"].min()
            risk = entry - sl
            if risk <= 0:
                return {"signal": None, "reason": "swing low tidak valid (SL >= entry)"}
            tp = entry + risk * RISK_REWARD_RATIO
            return {
                "signal": "BUY", "entry": entry, "sl": sl, "tp": tp,
                "reason": f"tren UP + pullback + bullish engulfing (RSI={curr['rsi']:.1f})",
            }

    elif trend == "DOWN":
        confirmed = _is_bearish_engulfing(prev, curr)
        rsi_ok = curr["rsi"] > RSI_OVERSOLD
        if confirmed and rsi_ok:
            entry = curr["close"]
            sl = swing_window["high"].max()
            risk = sl - entry
            if risk <= 0:
                return {"signal": None, "reason": "swing high tidak valid (SL <= entry)"}
            tp = entry - risk * RISK_REWARD_RATIO
            return {
                "signal": "SELL", "entry": entry, "sl": sl, "tp": tp,
                "reason": f"tren DOWN + pullback + bearish engulfing (RSI={curr['rsi']:.1f})",
            }

    return {"signal": None, "reason": "belum ada konfirmasi candle di area pullback"}

def check_signal_test_mode(df_h1: pd.DataFrame, df_m15: pd.DataFrame) -> dict:
    """
    MODE TESTING - buat verifikasi alur otomatisasi (data -> sinyal -> order) beneran jalan.
    Selalu BUY dengan SL/TP super ketat (lot minimum), TIDAK pakai logic strategi asli.
    JANGAN dipakai buat trading beneran - cuma buat tes pipeline sekali aja.
    """
    df_m15i = add_indicators_ltf(df_m15)
    curr = df_m15i.iloc[-1]

    if pd.isna(curr["atr"]) or curr["atr"] <= 0:
        return {"signal": None, "reason": "ATR belum siap, tunggu candle berikutnya"}

    entry = curr["close"]
    sl = entry - curr["atr"] * 0.3
    tp = entry + curr["atr"] * 0.5

    return {
        "signal": "BUY", "entry": entry, "sl": sl, "tp": tp,
        "reason": "MODE TESTING - paksa BUY buat verifikasi pipeline eksekusi",
    }
