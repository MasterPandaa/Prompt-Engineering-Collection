# Tetris Pygame

Game Tetris sederhana menggunakan Pygame.

## Fitur
- 7 bentuk tetromino (I, O, T, S, Z, J, L)
- Rotasi dengan wall-kick sederhana
- Grid 10x20
- Deteksi tabrakan (dinding, dasar, dan bidak lain)
- Pembersihan baris penuh dan perhitungan skor
- Hard drop, soft drop, pause

## Kontrol
- Left/Right: Geser kiri/kanan
- Down: Soft drop (turun cepat)
- Up / X: Rotasi searah jarum jam
- Z: Rotasi berlawanan jarum jam
- Space: Hard drop
- P: Pause/Resume

## Cara Menjalankan
1. Pastikan Python 3.8+ terpasang.
2. Instal dependensi:
   ```bash
   python -m pip install -r requirements.txt
   ```
3. Jalankan game:
   ```bash
   python tetris.py
   ```

Jika tampilan jendela terlalu besar/kecil, Anda dapat menyesuaikan `SCREEN_WIDTH`, `SCREEN_HEIGHT`, `BLOCK_SIZE` di `tetris.py`.

## Struktur Proyek
- `tetris.py` — kode utama game
- `requirements.txt` — dependensi Python
- `README.md` — petunjuk penggunaan
