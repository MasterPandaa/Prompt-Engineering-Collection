# Tetris (Python + Pygame)

Implementasi Tetris berbasis OOP dengan fitur Ghost Piece, line clearing efisien, skor/level sederhana, dan kontrol modern.

## Cara Menjalankan

1. Install depedensi (disarankan dalam virtualenv):

```
pip install -r requirements.txt
```

2. Jalankan game:

```
python tetris.py
```

## Kontrol

- Left/Right: Geser
- Down: Soft drop
- Space: Hard drop
- Z: Rotate CCW
- X / Up: Rotate CW
- P: Pause
- R: Restart
- Esc: Quit

## Catatan
- Level naik setiap 10 garis dibersihkan. Kecepatan jatuh meningkat seiring level.
- Ghost piece membantu memvisualisasikan posisi jatuh akhir.
- Line clearing diimplementasikan efisien dengan rebuild grid satu-pass.
