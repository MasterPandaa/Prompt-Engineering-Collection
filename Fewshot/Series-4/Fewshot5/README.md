# Tetris (Pygame)

Implementasi game Tetris menggunakan Pygame.

## Fitur
- 7 bentuk tetromino (I, O, T, S, Z, J, L) dengan rotasi.
- Grid 10x20 untuk gameplay.
- Deteksi tabrakan terhadap dinding, dasar, dan bidak lain.
- Pembersihan baris penuh dan perhitungan skor sederhana.
- Soft drop, hard drop, rotasi CW/CCW, dan percepatan level bertahap.

## Persyaratan
- Python 3.8+
- Pygame

Install dependensi:
```bash
pip install -r requirements.txt
```

## Menjalankan
```bash
python tetris.py
```

Kontrol:
- Panah Kiri/Kanan: geser bentuk
- Panah Bawah: soft drop
- Panah Atas atau X: rotate clockwise
- Z: rotate counter-clockwise
- Space: hard drop
- Enter (pada menu): mulai permainan

## Catatan
- Jendela permainan berukuran 450x600 (300x600 area bermain + 150 panel samping). 
- Kecepatan jatuh akan meningkat bertahap seiring jumlah piece yang spawn.
