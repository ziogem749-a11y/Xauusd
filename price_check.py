"""
Wrapper untuk WebSocket streaming TickerAll.
"""
from config import SYMBOL


def connect_stream(client, account_id: str):
    stream = client.stream.connect()
    stream.subscribe_ticks(account_id, [SYMBOL])
    print(f"Stream tick untuk {SYMBOL} berhasil disubscribe.")
    return stream


def get_latest_price(stream, account_id: str):
    try:
        tick = stream.latest_tick(SYMBOL)
        if tick is not None:
            return (tick.bid + tick.ask) / 2
    except Exception as e:
        print(f"DEBUG: error saat latest_tick(): {e}")

    try:
        tick = stream.wait_for_tick(SYMBOL, account_id=account_id, timeout=5)
        if tick is not None:
            return (tick.bid + tick.ask) / 2
    except Exception as e:
        print(f"DEBUG: error saat wait_for_tick(): {e}")

    return None
