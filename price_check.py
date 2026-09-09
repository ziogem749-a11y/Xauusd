"""
Ambil harga live sesaat (bid/ask) lewat streaming tick TickerAll.
Dipakai untuk 2 hal:
1. Melengkapi candle terakhir yang masih "berjalan" (belum closed) supaya RSI
   yang dihitung bot sedekat mungkin dengan yang ditampilkan live di MT5.
2. Cross-check harga sebelum kirim order (kalau selisih dari candle kegedean,
   order dibatalkan demi keamanan).
"""
import time
from config import SYMBOL

MAX_PRICE_DIFF = 2.0


def get_live_price(client, account_id: str, timeout_seconds: int = 5):
    price_holder = {"price": None}

    try:
        stream = client.stream.connect()

        def on_tick(event):
            if getattr(event, "symbol", None) == SYMBOL and price_holder["price"] is None:
                bid = getattr(event, "bid", None)
                ask = getattr(event, "ask", None)
                if bid is not None and ask is not None:
                    price_holder["price"] = (bid + ask) / 2

        stream.on("tick", on_tick)
        stream.subscribe_ticks(account_id, [SYMBOL])

        waited = 0
        while price_holder["price"] is None and waited < timeout_seconds:
            time.sleep(0.5)
            waited += 0.5

        stream.close()
    except Exception as e:
        print(f"Gagal ambil live price via stream: {e}")
        return None

    return price_holder["price"]


def is_price_reliable(candle_price: float, live_price) -> bool:
    if live_price is None:
        print("Tidak bisa ambil harga live buat verifikasi - order DIBATALKAN demi keamanan.")
        return False

    diff = abs(candle_price - live_price)
    print(f"Cross-check harga: candle={candle_price:.2f}, live={live_price:.2f}, selisih={diff:.2f}")

    if diff > MAX_PRICE_DIFF:
        print(f"⚠️ SELISIH TERLALU BESAR (>{MAX_PRICE_DIFF})! Order DIBATALKAN.")
        return False

    return True
