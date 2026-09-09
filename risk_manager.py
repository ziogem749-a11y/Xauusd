"""
Hitung lot size berdasarkan % risk dari equity akun, dan cek batas rugi harian.

PENTING: Akun HFM ini tipe CENT (XAUUSDc), artinya angka equity/balance yang
dibaca dari TickerAll itu dalam satuan US CENT, bukan USD (568 USC = $5.68 USD).
Makanya di sini dibagi 100 dulu supaya perhitungan risk-nya benar dalam USD.
"""
from config import RISK_PERCENT_PER_TRADE, MAX_DAILY_LOSS_PERCENT

VALUE_PER_PIP_PER_LOT = 1.0
CENT_ACCOUNT = True


def calculate_lot_size(equity_raw: float, entry: float, sl: float) -> float:
    equity_usd = equity_raw / 100 if CENT_ACCOUNT else equity_raw

    risk_amount = equity_usd * (RISK_PERCENT_PER_TRADE / 100)
    sl_distance_pips = abs(entry - sl) * 10

    if sl_distance_pips <= 0:
        return 0.0

    lot = risk_amount / (sl_distance_pips * VALUE_PER_PIP_PER_LOT)
    lot = max(0.01, round(lot, 2))
    lot = min(lot, 0.05)  # pengaman tambahan, jangan pernah lebih dari ini

    return lot


def daily_loss_exceeded(equity_start_of_day_raw: float, equity_now_raw: float) -> bool:
    if equity_start_of_day_raw <= 0:
        return False
    loss_percent = ((equity_start_of_day_raw - equity_now_raw) / equity_start_of_day_raw) * 100
    return loss_percent >= MAX_DAILY_LOSS_PERCENT
