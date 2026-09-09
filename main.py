"""
Loop utama bot. Ini yang dijalankan terus-terusan di Railway sebagai worker.
"""
import asyncio
import datetime

from config import CHECK_INTERVAL_SECONDS
from data_feed import DataFeed
from strategy import check_signal
from risk_manager import calculate_lot_size, daily_loss_exceeded
from executor import Executor


async def main():
    feed = DataFeed()
    await feed.connect()

    executor = Executor(feed.account)
    await executor.connect()

    account_info = await executor.get_account_info()
    equity_start_of_day = account_info["equity"]
    current_day = datetime.date.today()

    print("Bot mulai jalan. Memantau XAUUSD...")

    while True:
        try:
            today = datetime.date.today()
            if today != current_day:
                current_day = today
                account_info = await executor.get_account_info()
                equity_start_of_day = account_info["equity"]
                print(f"Hari baru: {today}. Reset patokan equity harian ke {equity_start_of_day}")

            account_info = await executor.get_account_info()
            equity_now = account_info["equity"]

            if daily_loss_exceeded(equity_start_of_day, equity_now):
                print("Batas rugi harian tercapai. Bot berhenti entry baru untuk hari ini.")
                await asyncio.sleep(CHECK_INTERVAL_SECONDS)
                continue

            if await executor.has_open_position():
                await asyncio.sleep(CHECK_INTERVAL_SECONDS)
                continue

            df = await feed.get_candles(limit=300)
            if df.empty:
                print("Data candle kosong, skip cek kali ini.")
                await asyncio.sleep(CHECK_INTERVAL_SECONDS)
                continue

            result = check_signal(df)

            if result["signal"] in ("BUY", "SELL"):
                lot = calculate_lot_size(equity_now, result["entry"], result["sl"])
                print(f"Sinyal {result['signal']} terdeteksi | entry={result['entry']} sl={result['sl']} tp={result['tp']} lot={lot}")
                await executor.place_order(result["signal"], lot, result["sl"], result["tp"])
            else:
                print(f"[{datetime.datetime.now()}] Belum ada sinyal.")

        except Exception as e:
            print(f"Error di loop utama: {e}")

        await asyncio.sleep(CHECK_INTERVAL_SECONDS)


if __name__ == "__main__":
    asyncio.run(main())
