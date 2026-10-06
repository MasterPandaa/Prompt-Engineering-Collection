# Pong (Python + Pygame)

Game Pong sederhana sesuai spesifikasi:
- Layar 800x600 piksel
- Paddle pemain (kiri) digerakkan dengan tombol `W` (atas) dan `S` (bawah)
- Paddle AI (kanan) otomatis mengikuti sumbu-Y bola
- Bola memantul pada dinding atas/bawah dan pada paddle
- Sistem skor: jika bola melewati sisi kiri, AI +1; jika melewati sisi kanan, Pemain +1

## Persiapan
1. Pastikan Python terpasang (disarankan Python 3.8+)
2. Install dependensi

Di Windows, jalankan salah satu perintah berikut dari folder proyek ini:

Menggunakan launcher `py` (disarankan di Windows):
```
py -m pip install -r requirements.txt
```

Atau menggunakan `python`:
```
python -m pip install -r requirements.txt
```

## Menjalankan Game
Menggunakan launcher `py`:
```
py main.py
```

Atau menggunakan `python`:
```
python main.py
```

## Kontrol
- `W`: Gerakkan paddle pemain ke atas
- `S`: Gerakkan paddle pemain ke bawah
- `Alt+F4` atau klik tombol close jendela untuk keluar

## Catatan
- Kecepatan AI dibatasi agar permainan tetap adil (`AI_SPEED`).
- Kecepatan bola (`BALL_SPEED`) dan dimensi paddle/bola dapat diubah pada konstanta di `main.py`.
