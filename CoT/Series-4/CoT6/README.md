# Tetris (Pygame)

Game Tetris sederhana berbasis Pygame.

## Fitur
- Grid 10x20, blok 30px
- 7 bentuk Tetris dengan rotasi
- Deteksi tabrakan dan wall-kick sederhana
- Soft drop, hard drop, rotasi, gerak kiri/kanan
- Line clear dan skor (dengan pengganda kuadrat)
- High score tersimpan ke `highscore.txt`

## Kontrol
- Panah Kiri/Kanan: Gerak piece
- Panah Bawah: Soft drop
- Panah Atas: Rotasi searah jarum jam
- Spasi: Hard drop
- Esc: Keluar
- Enter: Mulai permainan dari menu

## Menjalankan
1. Pastikan Python 3.9+ terpasang.
2. Instal dependensi:
   ```bash
   pip install -r requirements.txt
   ```
3. Jalankan game:
   ```bash
   python main.py
   ```

## Struktur File
- `main.py` — kode utama game
- `requirements.txt` — dependensi Python
- `README.md` — instruksi ini

## Catatan
- File `highscore.txt` akan dibuat otomatis di direktori yang sama saat game berakhir.
