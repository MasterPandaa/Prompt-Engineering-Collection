# Tetris (Pygame)

Game Tetris sederhana berbasis Pygame.

## Cara Menjalankan

1. Buat virtualenv (opsional namun direkomendasikan).
2. Install dependensi:

```bash
pip install -r requirements.txt
```

3. Jalankan game:

```bash
python tetris.py
```

## Kontrol

- Panah Kiri/Kanan: Gerak bidak.
- Panah Bawah: Soft drop.
- Panah Atas: Rotasi.
- Spasi: Hard drop.
- Esc: Keluar ke menu.

## Catatan

- Mekanika wall kick sederhana (geser 1 blok) untuk membantu rotasi dekat dinding.
- Skor bertambah berdasarkan jumlah garis yang dibersihkan sekaligus.
