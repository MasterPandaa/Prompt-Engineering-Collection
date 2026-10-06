# Pong (Python + Pygame)

Game Pong sederhana sesuai spesifikasi:
- Layar 800x600
- Paddle kiri: pemain (W = naik, S = turun)
- Paddle kanan: AI mengikuti posisi Y bola
- Bola memantul dari dinding atas/bawah atau paddle
- Sistem skor: bola lewat kiri = AI mendapat poin, bola lewat kanan = pemain mendapat poin

## Prasyarat
- Python 3.8+
- Pip

## Instalasi dependensi
Di direktori proyek:

```
pip install -r requirements.txt
```

Jika belum ada pip, gunakan installer Python resmi dan centang "Add Python to PATH" saat instalasi.

## Menjalankan game
Di direktori proyek:

```
python pong.py
```

Kontrol:
- W = naik
- S = turun
- Tutup jendela untuk keluar

## Catatan
- AI memiliki kecepatan sedikit lebih rendah daripada pemain agar permainan seimbang.
- Sudut pantulan bola bergantung pada titik kontak dengan paddle.
