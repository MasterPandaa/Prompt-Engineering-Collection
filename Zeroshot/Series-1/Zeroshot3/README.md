# Pong - Player vs AI (Pygame)

Ukuran layar: 800x600. Kontrol pemain (kiri): W untuk naik, S untuk turun. AI (kanan) otomatis mengikuti bola. Skor bertambah saat bola melewati sisi lawan.

## Instalasi

Pastikan Python 3.8+ terpasang. Lalu install dependensi:

```bash
python -m pip install -r requirements.txt
```

## Menjalankan

```bash
python pong.py
```

## Kontrol

- W: Gerak ke atas
- S: Gerak ke bawah
- Esc: Keluar

## Catatan

- Variabel seperti `AI_SPEED`, `PLAYER_SPEED`, dan `WIN_SCORE` bisa Anda sesuaikan di dalam file `pong.py`.
- Jika tampilan window tidak muncul di atas pada Windows, fokuskan jendela Pygame dari taskbar.
