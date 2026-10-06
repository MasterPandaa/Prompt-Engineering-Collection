# Tetris (Pygame)

Game Tetris sederhana berbasis Pygame.

## Cara Menjalankan

1. Buat dan aktifkan virtual environment (opsional, tapi disarankan).
2. Install dependensi:
   
   ```bash
   pip install -r requirements.txt
   ```

3. Jalankan game:
   
   ```bash
   python tetris.py
   ```

## Kontrol

- Panah Kiri/Kanan: Gerakkan bidak
- Panah Bawah: Soft drop (turun 1 step lebih cepat)
- Up atau X: Rotasi searah jarum jam (CW)
- Z: Rotasi berlawanan jarum jam (CCW)
- Space: Hard drop (jatuhkan langsung)
- ESC: Keluar

## Catatan

- Skor dan high score sederhana tersimpan di file `tetris_highscore.txt` (dibuat otomatis).
- Kecepatan jatuh meningkat setelah beberapa baris dibersihkan.
