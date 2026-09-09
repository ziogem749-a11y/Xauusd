import os

TICKERALL_API_KEY = os.environ.get("TICKERALL_API_KEY", "")
TICKERALL_ACCOUNT_ID = os.environ.get("TICKERALL_ACCOUNT_ID", "")

BROKER = os.environ.get("BROKER", "mt5")
MT_SERVER = os.environ.get("MT_SERVER", "HFMarketsGlobal-Live19")
MT_ACCOUNT = int(os.environ.get("MT_ACCOUNT", "229147194"))
MT_PASSWORD = os.environ.get("MT_PASSWORD", "")

SYMBOL = os.environ.get("SYMBOL", "XAUUSDc")
TIMEFRAME = os.environ.get("TIMEFRAME", "M5")

RSI_PERIOD = int(os.environ.get("RSI_PERIOD", 14))
RSI_OVERBOUGHT = float(os.environ.get("RSI_OVERBOUGHT", 70))
RSI_OVERSOLD = float(os.environ.get("RSI_OVERSOLD", 30))
ATR_PERIOD = int(os.environ.get("ATR_PERIOD", 14))
ATR_SL_MULTIPLIER = float(os.environ.get("ATR_SL_MULTIPLIER", 1.0))
RISK_REWARD_RATIO = float(os.environ.get("RISK_REWARD_RATIO", 1.5))

RISK_PERCENT_PER_TRADE = float(os.environ.get("RISK_PERCENT", 1.0))
MAX_DAILY_LOSS_PERCENT = float(os.environ.get("MAX_DAILY_LOSS_PERCENT", 3.0))
CHECK_INTERVAL_SECONDS = int(os.environ.get("CHECK_INTERVAL_SECONDS", 60))
TEST_MODE = os.environ.get("TEST_MODE", "false").lower() == "true"
