"""
Modul buat kirim order beneran ke MT5 lewat MetaAPI.
"""
from config import SYMBOL


class Executor:
    def __init__(self, account):
        self.account = account
        self.connection = None

    async def connect(self):
        self.connection = self.account.get_rpc_connection()
        await self.connection.connect()
        await self.connection.wait_synchronized()

    async def get_account_info(self) -> dict:
        info = await self.connection.get_account_information()
        return {"equity": info["equity"], "balance": info["balance"]}

    async def place_order(self, signal: str, lot: float, sl: float, tp: float):
        """
        signal: "BUY" atau "SELL"
        Mengirim market order dengan SL/TP yang sudah dihitung strategy + risk_manager.
        """
        try:
            if signal == "BUY":
                result = await self.connection.create_market_buy_order(
                    symbol=SYMBOL, volume=lot, stop_loss=sl, take_profit=tp,
                )
            elif signal == "SELL":
                result = await self.connection.create_market_sell_order(
                    symbol=SYMBOL, volume=lot, stop_loss=sl, take_profit=tp,
                )
            else:
                return None

            print(f"Order berhasil dikirim: {signal} {lot} lot {SYMBOL} | SL={sl} TP={tp}")
            return result
        except Exception as e:
            print(f"Gagal kirim order: {e}")
            return None

    async def has_open_position(self) -> bool:
        positions = await self.connection.get_positions()
        return any(p["symbol"] == SYMBOL for p in positions)
