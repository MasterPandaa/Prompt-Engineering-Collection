# Pong AI (Pygame)

Game Pong sederhana dengan lawan AI menggunakan Pygame.

## Fitur
- Kontrol pemain: `W` (naik) dan `S` (turun)
- AI mengikuti posisi Y bola dengan kecepatan terbatas
- Bola memantul dari dinding atas/bawah dan paddle
- Sistem skor otomatis ketika bola keluar sisi kiri/kanan

## Persyaratan
- Python 3.8+
- Pygame (lihat `requirements.txt`)

## Instalasi
1. (Opsional) Buat virtual environment.
2. Instal dependency:
   ```bash
   python -m pip install -r requirements.txt
   ```

## Menjalankan
```bash
python pong_ai.py
```

## Kontrol
- W: gerak paddle pemain ke atas
- S: gerak paddle pemain ke bawah
- Tutup jendela untuk keluar

## Struktur Kode
- `pong_ai.py` — file utama dengan kelas `Paddle`, `Ball`, serta loop game.
- `requirements.txt` — daftar dependensi.

Selamat bermain!
