"""
Loop utama bot - strategi Trend Pullback Entry (H1 tren + M15 timing entry).
"""
import time
import datetime
from tickerall import Tickerall

from config import (
    TICKERALL_API_KEY, BROKER, MT_SERVER, MT_ACCOUNT, MT_PASSWORD,
    CHECK_INTERVAL_SECONDS,
)
from data_feed import get_htf_candles, get_ltf_candles
from strategy import check_signal
from risk_manager import calculate_lot_size, daily_loss_exceeded
from executor import place_order, has_open_position, get_account_info


def main():
    client = Tickerall(api_key=TICKERALL_API_KEY)

    print("Menyambungkan ke broker HFM lewat TickerAll...")
    session = client.sessions.start(
        broker=BROKER, server=MT_SERVER, account=MT_ACCOUNT, password=MT_PASSWORD,
    )
    account_id = session.account_id
    print(f"Terhubung. Account ID: {account_id}")

    account_info = get_account_info(client, account_id)
    equity_start_of_day = account_info["equity"]
    current_day = datetime.date.today()

    print("Bot mulai jalan (strategi: Trend Pullback Entry). Memantau XAUUSD...")

    while True:
        try:
            today = datetime.date.today()
            if today != current_day:
                current_day = today
                account_info = get_account_info(client, account_id)
                equity_start_of_day = account_info["equity"]
                print(f"Hari baru: {today}. Reset patokan equity harian ke {equity_start_of_day}")

            account_info = get_account_info(client, account_id)
            equity_now = account_info["equity"]

            if daily_loss_exceeded(equity_start_of_day, equity_now):
                print("Batas rugi harian tercapai. Bot berhenti entry baru untuk hari ini.")
                time.sleep(CHECK_INTERVAL_SECONDS)
                continue

            if has_open_position(client, account_id):
                time.sleep(CHECK_INTERVAL_SECONDS)
                continue

            df_h1 = get_htf_candles(client, account_id, limit=300)
            df_m15 = get_ltf_candles(client, account_id, limit=300)

            if df_h1.empty or df_m15.empty:
                print("Data candle kosong (H1 atau M15), skip cek kali ini.")
                time.sleep(CHECK_INTERVAL_SECONDS)
                continue

            result = check_signal(df_h1, df_m15)

            if result["signal"] in ("BUY", "SELL"):
                lot = calculate_lot_size(equity_now, result["entry"], result["sl"])
                print(f"Sinyal {result['signal']} | entry={result['entry']:.2f} sl={result['sl']:.2f} "
                      f"tp={result['tp']:.2f} lot={lot} | {result['reason']}")
                place_order(client, account_id, result["signal"], lot, result["sl"], result["tp"])
            else:
                print(f"[{datetime.datetime.now()}] Belum ada sinyal ({result.get('reason', '')}).")

        except Exception as e:
            print(f"Error di loop utama: {e}")

        time.sleep(CHECK_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
