# Tetris (Python + Pygame)

Implementasi game Tetris klasik menggunakan Python dan Pygame.

## Spesifikasi
- Papan: 10 kolom x 20 baris
- Ukuran blok: 30 piksel
- 7 Tetromino: I, O, T, S, Z, J, L (warna berbeda)
- Kontrol:
  - Panah Kiri/Kanan: gerak horizontal
  - Panah Bawah: soft drop (percepat jatuh)
  - Panah Atas: rotasi searah jarum jam
  - Spasi: hard drop (jatuh langsung)
- Mekanisme inti:
  - Bidak spawn di tengah atas
  - Bidak terkunci saat menyentuh dasar/bidak lain
  - Line clearing & gravity (blok di atas turun)
- Skor:
  - 1 line: 100
  - 2 line: 300
  - 3 line: 500
  - 4 line (Tetris): 800
- Game Over: jika ada blok yang terkunci di area atas saat spawn berikutnya

## Cara Menjalankan (Windows)
1. Pastikan Python 3.8+ terinstal. Cek dengan:
   ```powershell
   python --version
   ```
2. (Opsional) Buat virtual environment:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\activate
   ```
3. Install dependensi:
   ```powershell
   pip install -r requirements.txt
   ```
4. Jalankan game:
   ```powershell
   python tetris.py
   ```

## Catatan
- Jika jendela tidak responsif, pastikan fokus pada jendela game.
- FPS ditargetkan 60; soft drop mempercepat gravitasi +/- 8x.
