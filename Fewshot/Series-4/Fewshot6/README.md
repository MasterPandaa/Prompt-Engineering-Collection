# Tetris (Pygame)

Implementasi game Tetris menggunakan Pygame dengan grid 10x20, 7 tetrominoes, rotasi, deteksi tabrakan, pembersihan baris, skor, dan tampilan Next Piece.

## Fitur
- 7 bentuk bidak (I, O, T, S, Z, J, L) dengan rotasi
- Grid 10 x 20
- Deteksi tabrakan dinding, dasar, dan bidak lain
- Pembersihan baris penuh + penurunan baris di atasnya
- Skor dan level sederhana (kecepatan naik otomatis)
- Tampilan Next Piece dan Game Over

## Persyaratan
- Python 3.8+
- Pygame

Instalasi dependensi:

```bash
pip install -r requirements.txt
```

## Menjalankan

```bash
python main.py
```

## Kontrol
- A / Left Arrow: Geser kiri
- D / Right Arrow: Geser kanan
- S / Down Arrow: Turun cepat (soft drop)
- W / Up Arrow / K: Rotasi searah jarum jam
- Space: Jatuhkan langsung (hard drop)
- P: Jeda / lanjut
- R: Mulai ulang ketika Game Over
- Esc: Keluar

## Catatan
- Pivot rotasi untuk setiap tetromino mengikuti definisi offset relatif dari contoh (titik (0,0) sebagai pivot), dengan wall-kick sederhana (coba geser -2..2 kolom saat rotasi).
