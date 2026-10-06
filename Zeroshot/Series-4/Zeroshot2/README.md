# Tetris (Python + Pygame)

Implementasi game Tetris klasik menggunakan Python dan Pygame.

## Spesifikasi
- Papan: 10 kolom x 20 baris
- Ukuran blok: 30px
- 7 Tetromino (I, O, T, S, Z, J, L) dengan warna berbeda
- Kontrol:
  - Panah Kiri/Kanan: geser bidak
  - Panah Bawah: soft drop (mempercepat jatuh)
  - Panah Atas: rotasi
  - SPACE: hard drop (langsung ke bawah)
- Line clearing dan skor
- Game over ketika bidak baru langsung bertabrakan di area atas

## Cara Menjalankan (Windows)
1. Pastikan Python 3.9+ terpasang.
2. Buat dan aktifkan virtual environment (opsional tapi disarankan):
   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```
3. Instal dependensi:
   ```powershell
   pip install -r requirements.txt
   ```
4. Jalankan game:
   ```powershell
   python tetris.py
   ```

## Catatan
- Jendela game berukuran 300x600 untuk area permainan + panel samping untuk skor dan preview bidak berikutnya.
- Skor: 1 baris=100, 2=300, 3=500, 4+=800.
- Ada sedikit percepatan gravitasi seiring waktu.
