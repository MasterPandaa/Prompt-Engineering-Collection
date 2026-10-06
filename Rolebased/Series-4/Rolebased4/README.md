# Tetris (Python + Pygame)

Implementasi klona Tetris OOP dengan Python dan Pygame, termasuk ghost piece, deteksi tabrakan efisien, dan line clearing tanpa lag.

## Persyaratan
- Python 3.9+
- Pygame

## Instalasi
```powershell
# Dari folder proyek ini
py -3 -m pip install -U pip
py -3 -m pip install -r requirements.txt
```

## Menjalankan
```powershell
py -3 tetris.py
```

## Kontrol
- Panah Kiri/Kanan: Geser bidak
- Panah Bawah: Soft drop
- Spasi: Hard drop
- Panah Atas / X: Rotasi searah jarum jam
- Z: Rotasi berlawanan jarum jam
- Esc: Keluar
- R: Restart saat Game Over

## Arsitektur
- `tetris.py`
  - `Piece`: bentuk, warna, posisi, rotasi.
  - `Board`: grid, collision, lock, ghost, line clear.
  - `Game`: loop, input, skor, HUD.

## Catatan
- Sistem randomizer 7-bag sederhana agar distribusi tetromino lebih adil.
- Gravity berbasis waktu sehingga frame-rate independen.
- Ghost piece digambar dengan warna direduksi.
