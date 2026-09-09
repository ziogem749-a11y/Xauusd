"""
Hitung ringkasan win rate dari riwayat trade yang sudah closed di broker (lewat TickerAll).
Data ini datang langsung dari histori broker, jadi tetap akurat walau Railway restart.
"""
from config import SYMBOL


def print_win_rate_summary(client, account_id: str, limit: int = 200):
    try:
        trades = client.history.get(account_id, symbol=SYMBOL, limit=limit)
    except Exception as e:
        print(f"Gagal ambil riwayat trade buat hitung win rate: {e}")
        return

    if not trades:
        print("Belum ada riwayat trade yang closed sama sekali.")
        return

    wins = 0
    losses = 0
    total_profit = 0.0
    skipped = 0

    for t in trades:
        profit = getattr(t, "profit", None)
        if profit is None:
            skipped += 1
            continue
        total_profit += profit
        if profit > 0:
            wins += 1
        elif profit < 0:
            losses += 1

    total = wins + losses
    win_rate = (wins / total * 100) if total else 0.0

    print("=" * 50)
    print("RINGKASAN WIN RATE (dari riwayat broker)")
    print("=" * 50)
    print(f"Total trade closed : {total}")
    print(f"Menang (WIN)       : {wins}")
    print(f"Kalah (LOSS)       : {losses}")
    print(f"Win rate           : {win_rate:.1f}%")
    print(f"Total profit/loss  : {total_profit:+.2f}")
    if skipped:
        print(f"(catatan: {skipped} trade dilewati karena data profit tidak terbaca)")
    print("=" * 50)
