"""
Kirim order beneran ke MT5 HFM lewat TickerAll.
"""
from config import SYMBOL


def place_order(client, account_id: str, signal: str, lot: float, sl: float, tp: float):
    try:
        order = client.orders.place(
            account_id,
            type="market",
            symbol=SYMBOL,
            side=signal,
            volume=lot,
            stop_loss=sl,
            take_profit=tp,
        )
        print(f"Order berhasil: ticket={order.ticket} status={order.status}")
        return order
    except Exception as e:
        print(f"Gagal kirim order: {e}")
        return None


def has_open_position(client, account_id: str) -> bool:
    detail = client.accounts.get(account_id)
    return any(p.symbol == SYMBOL for p in detail.positions)


def get_account_info(client, account_id: str) -> dict:
    detail = client.accounts.get(account_id)
    return {"equity": detail.equity, "balance": detail.balance}
