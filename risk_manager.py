"""
Hitung lot size berdasarkan % risk dari equity akun, dan cek batas rugi harian.
"""
from config import RISK_PERCENT_PER_TRADE, MAX_DAILY_LOSS_PERCENT

# Nilai per pip per 1.0 lot untuk XAUUSD umumnya $1/pip (tergantung broker, CEK ke HFM!)
VALUE_PER_PIP_PER_LOT = 1.0


def calculate_lot_size(equity: float, entry: float, sl: float) -> float:
    """
    Hitung lot size supaya kalau SL kena, kerugian = RISK_PERCENT_PER_TRADE dari equity.
    """
    risk_amount = equity * (RISK_PERCENT_PER_TRADE / 100)
    sl_distance_pips = abs(entry - sl) * 10  # untuk XAUUSD, 1 pip = 0.1 biasanya, CEK spesifikasi HFM

    if sl_distance_pips <= 0:
        return 0.0

    lot = risk_amount / (sl_distance_pips * VALUE_PER_PIP_PER_LOT)

    # Bulatkan ke 0.01 terdekat (lot minimum umum), dan jangan pernah 0
    lot = max(0.01, round(lot, 2))
    return lot


def daily_loss_exceeded(equity_start_of_day: float, equity_now: float) -> bool:
    """Cek apakah kerugian hari ini sudah melewati batas MAX_DAILY_LOSS_PERCENT."""
    if equity_start_of_day <= 0:
        return False
    loss_percent = ((equity_start_of_day - equity_now) / equity_start_of_day) * 100
    return loss_percent >= MAX_DAILY_LOSS_PERCENT
