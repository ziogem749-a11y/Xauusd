import os

TICKERALL_API_KEY = os.environ.get("TICKERALL_API_KEY", "")
TICKERALL_ACCOUNT_ID = os.environ.get("TICKERALL_ACCOUNT_ID", "")

BROKER = os.environ.get("BROKER", "mt5")
MT_SERVER = os.environ.get("MT_SERVER", "HFMarketsGlobal-Live19")
MT_ACCOUNT = int(os.environ.get("MT_ACCOUNT", "229147194"))
MT_PASSWORD = os.environ.get("MT_PASSWORD", "")

SYMBOL = os.environ.get("SYMBOL", "XAUUSDc")
TIMEFRAME_TREND = os.environ.get("TIMEFRAME_TREND", "H1")
TIMEFRAME_ENTRY = os.environ.get("TIMEFRAME_ENTRY", "M15")

EMA_TREND_FAST = int(os.environ.get("EMA_TREND_FAST", 50))
EMA_TREND_SLOW = int(os.environ.get("EMA_TREND_SLOW", 200))
EMA_PULLBACK = int(os.environ.get("EMA_PULLBACK", 21))
RSI_PERIOD = int(os.environ.get("RSI_PERIOD", 14))
RSI_OVERBOUGHT = float(os.environ.get("RSI_OVERBOUGHT", 70))
RSI_OVERSOLD = float(os.environ.get("RSI_OVERSOLD", 30))
SWING_LOOKBACK = int(os.environ.get("SWING_LOOKBACK", 10))
RISK_REWARD_RATIO = float(os.environ.get("RISK_REWARD_RATIO", 2.0))
PULLBACK_TOLERANCE_ATR = float(os.environ.get("PULLBACK_TOLERANCE_ATR", 0.5))
ATR_PERIOD = int(os.environ.get("ATR_PERIOD", 14))

RISK_PERCENT_PER_TRADE = float(os.environ.get("RISK_PERCENT", 1.0))
MAX_DAILY_LOSS_PERCENT = float(os.environ.get("MAX_DAILY_LOSS_PERCENT", 3.0))
CHECK_INTERVAL_SECONDS = int(os.environ.get("CHECK_INTERVAL_SECONDS", 60))
TEST_MODE = os.environ.get("TEST_MODE", "false").lower() == "true"
