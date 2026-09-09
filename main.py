"""
Loop utama bot - strategi RSI Reversal, sinyal lebih sering, RR ketat 1:1.5.
RSI dihitung termasuk candle "hidup" (harga live) supaya sedekat mungkin
dengan yang ditampilkan real-time di MT5.
Otomatis cetak ringkasan win rate tiap kali posisi baru saja closed.

PAUSE_TRADING=true di Railway Variables -> bot tetap jalan mantau & print data,
TAPI TIDAK kirim order sama sekali.
"""
import os
import time
import datetime
from tickerall import Tickerall

from config import (
    TICKERALL_API_KEY, BROKER, MT_SERVER, MT_ACCOUNT, MT_PASSWORD,
    CHECK_INTERVAL_SECONDS, TIMEFRAME,
)
from data_feed import get_candles, append_live_candle
from strategy import check_signal
from risk_manager import calculate_lot_size, daily_loss_exceeded
from executor import place_order, has_open_position, get_account_info
from stats import print_win_rate_summary
from price_check import get_live_price, is_price_reliable

PAUSE_TRADING = os.environ.get("PAUSE_TRADING", "false").lower() == "true"


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

    was_position_open = has_open_position(client, account_id)

    print(f"Bot mulai jalan (strategi: RSI Reversal {TIMEFRAME}). Memantau XAUUSD...")
    if PAUSE_TRADING:
        print("⏸️  PAUSE_TRADING AKTIF - bot HANYA memantau & print data, TIDAK akan kirim order.")
    if was_position_open:
        print("Catatan: sudah ada posisi terbuka saat bot start.")

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

            is_position_open_now = has_open_position(client, account_id)

            if was_position_open and not is_position_open_now:
                print("Posisi baru saja closed. Menghitung ringkasan win rate terbaru...")
                print_win_rate_summary(client, account_id)

            was_position_open = is_position_open_now

            if is_position_open_now:
                time.sleep(CHECK_INTERVAL_SECONDS)
                continue

            df_closed = get_candles(client, account_id, limit=300)
            if df_closed.empty:
                print("Data candle kosong, skip cek kali ini.")
                time.sleep(CHECK_INTERVAL_SECONDS)
                continue

            live_price = get_live_price(client, account_id)
            df = append_live_candle(df_closed, live_price)

            result = check_signal(df)

            last_candle_time = df["time"].iloc[-1]
            last_close = df["close"].iloc[-1]

            if result["signal"] in ("BUY", "SELL"):
                lot = calculate_lot_size(equity_now, result["entry"], result["sl"])
                print(f"Sinyal {result['signal']} | entry={result['entry']:.2f} sl={result['sl']:.2f} "
                      f"tp={result['tp']:.2f} lot={lot} | {result['reason']}")

                if PAUSE_TRADING:
                    print("⏸️  PAUSE_TRADING aktif - order TIDAK dikirim (mode observasi saja).")
                elif not is_price_reliable(result["entry"], live_price):
                    print("Order dibatalkan karena data harga dicurigai tidak akurat.")
                else:
                    order = place_order(client, account_id, result["signal"], lot, result["sl"], result["tp"])
                    if order is not None:
                        was_position_open = True
            else:
                print(f"[{datetime.datetime.now()}] Belum ada sinyal ({result.get('reason', '')}). "
                      f"[live_price={live_price}, candle_terakhir={last_candle_time}, close={last_close:.2f}]")

        except Exception as e:
            print(f"Error di loop utama: {e}")

        time.sleep(CHECK_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
