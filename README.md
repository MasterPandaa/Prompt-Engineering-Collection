# Pong (Pygame)

Implementasi game Pong sederhana dan bersih menggunakan Pygame dengan OOP, AI lawan yang adil, dan fisika pantulan akurat.

## Fitur
- Layar 800x600, 60 FPS.
- Kelas `Paddle` dan `Ball` untuk struktur OOP yang jelas.
- Kontrol pemain: `W` (naik) dan `S` (turun).
- AI lawan (paddle kanan) dengan reaksi tertunda dan error margin sehingga bisa dikalahkan.
- Fisika pantulan bola akurat dari dinding dan paddle.
- Sistem skor, garis tengah putus-putus, info kontrol.
- Menang di skor 11. Tekan `R` untuk reset setelah kemenangan. `ESC` untuk keluar.

## Persyaratan
- Python 3.9+
- Pygame (lihat `requirements.txt`)

## Instalasi
Disarankan menggunakan virtual environment.

```bash
# 1) Buat dan aktifkan virtual env (Windows PowerShell)
python -m venv .venv
.venv\Scripts\Activate.ps1

# 2) Install dependencies
pip install -r requirements.txt
```

## Menjalankan Game
```bash
python pong.py
```

## Struktur Kode Singkat
- `pong.py` — berisi implementasi lengkap game:
  - `Paddle` — logika paddle, gerak, AI follow.
  - `Ball` — update posisi, pantulan, reset, refleksi dari paddle.
  - `ScoreBoard` — tampilan skor dan reset.
  - `PongGame` — loop utama: input, update, draw, AI, skor.
- `requirements.txt` — daftar dependensi.

## Kontrol
- `W` / `S` — gerakkan paddle kiri.
- `R` — reset setelah ada pemenang.
- `ESC` — keluar.

## Catatan AI
AI memprediksi posisi Y bola dengan sampling berkala, menerapkan error margin acak, dan reaksi bertahap (easing) serta dibatasi kecepatan paddle sehingga terasa menantang namun tetap adil.

## Lisensi
MIT
