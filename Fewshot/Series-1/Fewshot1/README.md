# Pong dengan AI (Pygame)

Game Pong sederhana menggunakan Pygame. Paddle kiri dikendalikan pemain (W/S), paddle kanan dikendalikan AI yang mengikuti bola.

## Fitur
- Layar 800x600.
- Kelas `Paddle` (pemain & AI) dan `Ball`.
- Kontrol pemain kiri dengan `W` (naik) dan `S` (turun).
- AI mengikuti posisi Y bola dengan kecepatan maksimum agar terasa natural.
- Pantulan bola dari tepi dan paddle dengan variasi sudut berdasarkan titik benturan.
- Sistem skor dan reset bola setelah poin.

## Persyaratan
- Python 3.8+
- Pygame

## Instalasi
```
pip install -r requirements.txt
```

## Menjalankan
```
python pong_ai.py
```

## Kontrol
- W: Gerakkan paddle kiri ke atas
- S: Gerakkan paddle kiri ke bawah
- Esc: Keluar dari permainan

## Struktur Berkas
- `pong_ai.py` — kode utama game.
- `requirements.txt` — dependensi Python.
- `README.md` — panduan penggunaan.
