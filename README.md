# Tetris (Pygame)

Game Tetris sederhana menggunakan Pygame dengan grid 10x20, 7 bentuk tetromino, rotasi, deteksi tabrakan, pembersihan baris, next piece, dan skor.

## Fitur
- 7 tetromino (I, O, T, S, Z, J, L) dengan rotasi.
- Grid 10x20 dan ukuran blok 30 piksel.
- Deteksi tabrakan dinding, dasar, dan bidak lain.
- Pembersihan baris penuh dan pergeseran baris di atasnya.
- Next piece preview dan skor.
- Kontrol: panah kiri/kanan (gerak), panah atas (rotasi), panah bawah (soft drop), spasi (hard drop).

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

## Catatan
- Kecepatan jatuh meningkat seiring waktu. 
- Jika ingin mengubah ukuran blok atau grid, sesuaikan konstanta di bagian atas `tetris.py`.
