# Pong (Python + Pygame)

Game Pong sederhana sesuai spesifikasi:
- Layar: 800 x 600 px
- Paddle Kiri: Kontrol pemain (W = naik, S = turun)
- Paddle Kanan (AI): Mengikuti posisi Y bola secara otomatis
- Bola memantul dari dinding atas/bawah dan paddle
- Sistem skor ditampilkan di layar

## Persyaratan
- Python 3.8+
- Pygame

## Instalasi
1. (Opsional) Disarankan menggunakan virtual environment.
2. Instal dependensi:
   ```bash
   pip install -r requirements.txt
   ```

## Cara Menjalankan
Jalankan perintah berikut di direktori proyek:
```bash
python pong.py
```

## Kontrol
- W: Naik
- S: Turun
- ESC: Keluar

## Catatan
- AI memiliki kecepatan sedikit lebih lambat dari pemain agar permainan lebih seimbang.
- Kecepatan bola meningkat perlahan setiap kali memantul dari paddle dan sudut pantulan dipengaruhi titik kontak pada paddle.
