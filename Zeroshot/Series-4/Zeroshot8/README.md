# Tetris (Pygame)

Implementasi game Tetris klasik menggunakan Python dan Pygame.

## Fitur
- Papan 10 x 20 dengan ukuran blok 30 piksel
- 7 Tetromino (I, O, T, S, Z, J, L) dengan warna berbeda
- Kontrol:
  - Panah Kiri/Kanan: geser bidak
  - Panah Atas: rotasi
  - Panah Bawah: soft drop (lebih cepat turun)
  - Space: hard drop (langsung ke bawah)
  - ESC: keluar
  - R: restart (saat game over)
- Mekanisme penguncian bidak, clearing baris, skor, level, dan game over

## Instalasi
1. Pastikan Python 3.8+ terpasang.
2. Buat virtual environment (opsional namun disarankan):
   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```
3. Install dependency:
   ```powershell
   pip install -r requirements.txt
   ```

## Menjalankan
```powershell
python tetris.py
```

Selamat bermain!
