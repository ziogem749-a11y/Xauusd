# XAUUSD Auto-Execution Bot

Bot trading otomatis untuk XAUUSD, strategi EMA Trend Filter + Asia Session Breakout + ATR SL/TP, dieksekusi lewat MetaAPI ke akun MT5 (HFM).

## PENTING sebelum jalan

1. Nama method MetaAPI SDK di sini adalah skeleton berdasarkan pola umum SDK. Sebelum deploy, cek dokumentasi resmi terbaru di https://metaapi.cloud/docs/client/
2. Jalankan di DEMO account dulu, minimal 1-2 minggu, sebelum pakai akun real.
3. Cek spesifikasi pip/lot XAUUSD di HFM (nilai per pip per lot bisa beda dari asumsi di risk_manager.py).
4. Free tier MetaAPI ada batasan (jumlah akun, request/bulan).
