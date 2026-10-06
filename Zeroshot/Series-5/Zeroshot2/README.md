# Pygame Chess (Tanpa Gambar Eksternal)

Game catur standar dengan Python dan Pygame. Bidak dirender menggunakan Unicode Chess Symbols (tanpa gambar .png). Jika font simbol catur tidak tersedia di sistem, aplikasi otomatis jatuh ke bentuk geometri sederhana.

## Fitur
- Papan 8x8 warna selang-seling.
- Gerak dasar lengkap: Pion, Benteng, Kuda, Gajah, Ratu, Raja.
- Sistem giliran: Putih (Player) lalu Hitam (AI).
- Deteksi skak (check) dan penapisan langkah legal sehingga raja tidak ditinggal dalam skak.
- Promosi pion otomatis ke Ratu.
- AI Hitam sederhana: memilih langkah terbaik 1-ply berdasarkan evaluasi material (tie-break acak).
- Interaksi mouse: klik bidak putih, lalu klik petak tujuan.

## Cara Menjalankan
1. Pastikan Python 3.9+ terpasang.
2. Install dependensi:
   ```bash
   pip install -r requirements.txt
   ```
3. Jalankan game:
   ```bash
   python chess_pygame.py
   ```

## Catatan
- Castling dan en-passant tidak diimplementasikan demi kesederhanaan.
- Deteksi akhir permainan: skakmat dan stalemate ditampilkan di status bar.
- Untuk tampilan simbol catur, aplikasi mencoba beberapa font umum: DejaVu Sans, Segoe UI Symbol, Arial Unicode MS, Symbola, Noto Sans Symbols2, dll. Jika tidak ada yang tersedia, program menggambar bentuk geometri sebagai fallback.
