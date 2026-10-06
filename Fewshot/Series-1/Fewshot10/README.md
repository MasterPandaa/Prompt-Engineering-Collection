# Pong dengan AI (Pygame)

Game Pong sederhana menggunakan Pygame dengan AI pada paddle kanan.

## Fitur
- Layar 800x600.
- Kelas `Paddle` (pemain kiri dan AI kanan) dan `Ball`.
- Kontrol pemain: `W` (naik) dan `S` (turun).
- AI mengikuti posisi Y bola (kecepatan dibatasi agar tidak mustahil dikalahkan).
- Pantulan bola pada dinding dan paddle dengan sedikit percepatan tiap mengenai paddle.
- Sistem skor. Default kemenangan: 10 poin.

## Persyaratan
- Python 3.8+
- Pygame

Instal dependensi:

```bash
pip install -r requirements.txt
```

## Menjalankan

```bash
python pong.py
```

## Kontrol
- `W`: Gerakkan paddle kiri ke atas.
- `S`: Gerakkan paddle kiri ke bawah.
- `ESC`: Keluar dari permainan.

## Catatan
- Jika jendela tidak muncul atau terjadi error terkait display, pastikan Anda menjalankan di lingkungan desktop (bukan headless) dan driver grafis sudah terpasang.
- Nilai `SCORE_TO_WIN`, `AI_MAX_SPEED`, dan kecepatan bola awal dapat disesuaikan di bagian parameter permainan di dalam `pong.py`.
