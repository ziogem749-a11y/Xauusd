"""
Lot size TETAP (fixed), tidak dihitung dinamis - lebih simpel dan predictable
untuk modal kecil di akun cent.
"""
from config import MAX_DAILY_LOSS_PERCENT

FIXED_LOT_SIZE = 0.02


def calculate_lot_size(equity_raw: float, entry: float, sl: float) -> float:
    """Selalu return lot tetap, tidak peduli equity atau jarak SL."""
    return FIXED_LOT_SIZE


def daily_loss_exceeded(equity_start_of_day_raw: float, equity_now_raw: float) -> bool:
    if equity_start_of_day_raw <= 0:
        return False
    loss_percent = ((equity_start_of_day_raw - equity_now_raw) / equity_start_of_day_raw) * 100
    return loss_percent >= MAX_DAILY_LOSS_PERCENT
