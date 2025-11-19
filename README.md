# Pong dengan AI (Pygame)

Game Pong sederhana dengan AI menggunakan Pygame.

## Persyaratan
- Python 3.8+
- Pygame

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

## Cara Menjalankan

```bash
python pong_ai.py
```

## Kontrol
- W: Gerak ke atas (paddle kiri)
- S: Gerak ke bawah (paddle kiri)
- R: Reset ketika ada pemenang
- Tutup jendela untuk keluar

## Catatan
- Kecepatan AI disetel melalui variabel `ai_max_speed` di `pong_ai.py`.
- Atur `max_score` menjadi `None` jika ingin bermain tanpa batas skor.
