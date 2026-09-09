"""
Konfigurasi bot, semua diambil dari environment variables.
JANGAN hardcode token/password di sini — set lewat Railway Variables.
"""
import os

# --- MetaAPI ---
METAAPI_TOKEN = os.environ.get("METAAPI_TOKEN", "")
METAAPI_ACCOUNT_ID = os.environ.get("METAAPI_ACCOUNT_ID", "")

# --- Trading ---
SYMBOL = os.environ.get("SYMBOL", "XAUUSD")
TIMEFRAME = os.environ.get("TIMEFRAME", "15m")  # candle timeframe untuk analisa

# --- Strategi ---
EMA_FAST = int(os.environ.get("EMA_FAST", 50))
EMA_SLOW = int(os.environ.get("EMA_SLOW", 200))
ATR_PERIOD = int(os.environ.get("ATR_PERIOD", 14))
ATR_SL_MULTIPLIER = float(os.environ.get("ATR_SL_MULTIPLIER", 1.5))
ATR_TP_MULTIPLIER = float(os.environ.get("ATR_TP_MULTIPLIER", 2.5))

# Jam range sesi Asia (WIB / UTC+7) yang dipakai sebagai basis breakout
ASIA_SESSION_START_HOUR_WIB = int(os.environ.get("ASIA_START", 0))
ASIA_SESSION_END_HOUR_WIB = int(os.environ.get("ASIA_END", 7))

# --- Risk Management ---
RISK_PERCENT_PER_TRADE = float(os.environ.get("RISK_PERCENT", 1.0))  # % dari equity
MAX_DAILY_LOSS_PERCENT = float(os.environ.get("MAX_DAILY_LOSS_PERCENT", 3.0))

# --- Loop ---
CHECK_INTERVAL_SECONDS = int(os.environ.get("CHECK_INTERVAL_SECONDS", 60))
