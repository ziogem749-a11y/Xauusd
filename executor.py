"""
Kirim order beneran ke MT5 HFM lewat TickerAll.
Ada auto-retry kalau kena error SYMBOL_NOT_FOUND (kadang transient/sesaat).
"""
import time
from config import SYMBOL


def place_order(client, account_id: str, signal: str, lot: float, sl: float, tp: float, max_retries: int = 3):
    for attempt in range(1, max_retries + 1):
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
            print(f"Order berhasil (percobaan {attempt}): ticket={order.ticket} status={order.status}")
            return order
        except Exception as e:
            print(f"Gagal kirim order (percobaan {attempt}/{max_retries}): {e}")
            if attempt < max_retries:
                time.sleep(3)

    print(f"Order GAGAL setelah {max_retries}x percobaan. Kemungkinan masalah dari sisi TickerAll/broker.")
    return None


def get_open_positions_detail(client, account_id: str):
    detail = client.accounts.get(account_id)
    return detail.positions or []


def has_open_position(client, account_id: str) -> bool:
    positions = get_open_positions_detail(client, account_id)
    return any(getattr(p, "symbol", None) == SYMBOL for p in positions)


def get_account_info(client, account_id: str) -> dict:
    detail = client.accounts.get(account_id)
    info = detail.account
    return {"equity": info.equity, "balance": info.balance}
