"""
Modul buat konek ke MetaAPI dan ambil data candle XAUUSD.
Butuh: pip install metaapi-cloud-sdk pandas
"""
import pandas as pd
from metaapi_cloud_sdk import MetaApi

from config import METAAPI_TOKEN, METAAPI_ACCOUNT_ID, SYMBOL, TIMEFRAME


class DataFeed:
    def __init__(self):
        self.api = MetaApi(METAAPI_TOKEN)
        self.account = None

    async def connect(self):
        """Ambil handle akun MT5 dan pastikan sudah deployed/connected."""
        self.account = await self.api.metatrader_account_api.get_account(METAAPI_ACCOUNT_ID)

        if self.account.state != "DEPLOYED":
            await self.account.deploy()

        print("Menunggu koneksi ke broker...")
        await self.account.wait_connected()
        print("Akun MT5 terkoneksi ke MetaAPI.")

    async def get_candles(self, limit: int = 300) -> pd.DataFrame:
        """
        Ambil N candle terakhir untuk SYMBOL & TIMEFRAME dari config.
        Return DataFrame dengan kolom: time, open, high, low, close, volume
        """
        candles = await self.account.get_historical_candles(
            symbol=SYMBOL,
            timeframe=TIMEFRAME,
            start_time=None,
            limit=limit,
        )

        df = pd.DataFrame(candles)
        if df.empty:
            return df

        df = df.rename(columns={
            "time": "time",
            "open": "open",
            "high": "high",
            "low": "low",
            "close": "close",
            "tickVolume": "volume",
        })
        df["time"] = pd.to_datetime(df["time"])
        df = df.sort_values("time").reset_index(drop=True)
        return df[["time", "open", "high", "low", "close", "volume"]]

    async def get_current_price(self) -> dict:
        """Ambil harga bid/ask terkini untuk SYMBOL."""
        price = await self.account.get_symbol_price(SYMBOL)
        return {"bid": price["bid"], "ask": price["ask"], "time": price["time"]}
