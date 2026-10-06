# Snake Game (Pygame)

Game Snake klasik dibuat dengan Python dan Pygame.

## Persyaratan
- Python 3.8+
- Windows

## Instalasi
Disarankan menggunakan virtual environment (opsional namun direkomendasikan).

1) Buat dan aktifkan virtual environment (opsional):
```
python -m venv .venv
.\.venv\Scripts\activate
```

2) Instal dependensi:
```
pip install -r requirements.txt
```

## Menjalankan Game
```
python snake_game.py
```

## Kontrol
- Panah/WASD untuk bergerak
- Saat Game Over:
  - R / Space: Restart
  - Q / Esc: Keluar

## Catatan
- Ubah `SPEED`, `BLOCK_SIZE`, atau ukuran layar (`WIDTH`, `HEIGHT`) di `snake_game.py` sesuai preferensi.
- Anda dapat mengaktifkan garis grid untuk debugging dengan membuka komentar pada `draw_grid(screen)` di fungsi render.
