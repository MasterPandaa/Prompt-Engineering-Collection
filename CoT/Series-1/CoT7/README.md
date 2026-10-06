# Pong dengan AI (Pygame)

Game Pong sederhana dengan satu pemain melawan AI menggunakan Pygame.

## Cara Menjalankan

1) Buat dan aktifkan virtualenv (opsional namun direkomendasikan).
2) Install dependensi:

```bash
pip install -r requirements.txt
```

3) Jalankan game:

```bash
python pong_ai.py
```

## Kontrol
- W: Gerakkan paddle pemain ke atas
- S: Gerakkan paddle pemain ke bawah

## Catatan
- AI dilengkapi dead zone kecil agar tidak terlalu sempurna.
- Kecepatan dapat disesuaikan melalui konstanta di bagian atas `pong_ai.py`.
