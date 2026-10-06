# Tetris (Pygame)

Game Tetris sederhana berbasis Pygame.

## Fitur
- 7 bentuk tetromino (I, O, T, S, Z, J, L) dengan rotasi.
- Grid permainan 10x20.
- Deteksi tabrakan (dinding, dasar, dan bidak terkunci).
- Pembersihan baris dan perhitungan skor.
- Preview bidak berikutnya.

## Kontrol
- Panah Kiri/Kanan: Geser bidak.
- Panah Bawah: Turunkan bidak satu langkah.
- Panah Atas: Rotasi bidak (dengan wall kick sederhana).
- Spasi: Hard drop (jatuhkan langsung).
- Esc: Keluar.

## Menjalankan
1. Pastikan Python 3.8+ terpasang.
2. Install dependensi:
   ```bash
   pip install -r requirements.txt
   ```
3. Jalankan game:
   ```bash
   python tetris.py
   ```

Selamat bermain!
