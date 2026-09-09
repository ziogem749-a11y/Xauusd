"""
Kirim order beneran ke MT5 HFM lewat TickerAll.
"""
from config import SYMBOL


def _get_attr_any(obj, names, default=None):
    """Coba beberapa kemungkinan nama field, return yang pertama ketemu."""
    for name in names:
        if hasattr(obj, name):
            return getattr(obj, name)
    return default


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
    positions = _get_attr_any(detail, ["positions"], [])
    return any(getattr(p, "symbol", None) == SYMBOL for p in positions)


def get_account_info(client, account_id: str) -> dict:
    detail = client.accounts.get(account_id)

    equity = _get_attr_any(detail, ["equity", "account_equity", "acc_equity", "eq"])
    balance = _get_attr_any(detail, ["balance", "account_balance", "acc_balance", "bal"])

    if equity is None or balance is None:
        print("DEBUG: field equity/balance gak ketemu. Struktur objek AccountDetail:")
        print(vars(detail) if hasattr(detail, "__dict__") else dir(detail))
        equity = equity or 0
        balance = balance or 0

    return {"equity": equity, "balance": balance}
