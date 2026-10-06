# Tetris (Python + Pygame)

Game Tetris klasik dibuat dengan Python dan Pygame.

## Spesifikasi Utama
- Grid/Papan: 10 kolom x 20 baris.
- Ukuran blok: 30 piksel per blok.
- 7 Tetromino: I, O, T, S, Z, J, L (tiap bentuk punya warna berbeda).
- Kontrol:
  - Panah Kiri/Kanan: Geser bidak.
  - Panah Bawah: Soft drop (percepat turun).
  - Panah Atas: Rotasi.
  - Space: Hard drop (jatuh langsung).
  - Enter: Restart (saat Game Over).
  - Esc: Keluar dari game.
- Mekanisme: Lock piece saat menyentuh dasar/stack, line clearing, skor berdasarkan jumlah baris yang dibersihkan sekaligus.
- Game Over: Jika bidak baru tidak bisa muncul karena papan penuh.

## Persyaratan
- Python 3.8+
- Pygame (akan diinstal via `requirements.txt`)

## Cara Menjalankan (Windows)
1. Buka terminal di folder proyek ini.
2. Install dependensi:
   ```bat
   py -m pip install -r requirements.txt
   ```
3. Jalankan game:
   ```bat
   py tetris.py
   ```

Jika Anda menggunakan virtual environment, aktifkan terlebih dahulu sebelum langkah instalasi.

## Catatan
- Saat tombol Panah Bawah ditahan, kecepatan jatuh otomatis dipercepat.
- Skor: 1/2/3/4 baris sekaligus = 100/300/500/800 poin.
