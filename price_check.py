"""
Wrapper untuk WebSocket streaming TickerAll - dipakai untuk dapat harga live
(bid/ask) yang TIDAK PERNAH beku, beda dari candles.get() yang polling HTTP
biasa (rentan macet saat ada reconnect window ke broker).

Sesuai contoh resmi dari tim TickerAll:
- stream.connect() sekali di awal - jalan di thread background, auto-reconnect
- stream.latest_tick(symbol) - baca cache O(1), tidak perlu polling jaringan
"""
from config import SYMBOL


def connect_stream(client, account_id: str):
    stream = client.stream.connect()
    stream.subscribe_ticks(account_id, [SYMBOL])
    print(f"Stream tick untuk {SYMBOL} berhasil disubscribe.")
    return stream


def get_latest_price(stream):
    tick = stream.latest_tick(SYMBOL)
    if tick is None:
        return None
    return (tick.bid + tick.ask) / 2
