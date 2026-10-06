# Pong AI (Pygame)

Game Pong sederhana dengan satu pemain melawan AI berbasis logika pelacakan bola. Dibuat menggunakan Pygame.

## Fitur
- Paddle pemain (kiri) digerakkan dengan tombol `W` (naik) dan `S` (turun).
- Paddle AI (kanan) otomatis mengikuti posisi Y bola dengan kecepatan terbatas.
- Bola memantul pada dinding atas/bawah dan pada paddle, dengan variasi sudut (spin) berdasar titik tumbuk.
- Sistem skor: poin bertambah saat bola keluar dari sisi lawan.

## Persyaratan
- Python 3.8+
- Pygame (lihat `requirements.txt`)

## Instalasi

1. Aktifkan virtual environment (opsional namun direkomendasikan)
   - Windows (PowerShell):
     ```powershell
     python -m venv .venv
     .venv\Scripts\Activate.ps1
     ```

2. Instal dependensi:
   ```powershell
   pip install -r requirements.txt
   ```

## Menjalankan

Dari direktori proyek, jalankan:
```powershell
python main.py
```

## Kontrol
- `W` : Gerakkan paddle pemain ke atas
- `S` : Gerakkan paddle pemain ke bawah
- `X` : Tutup jendela game (klik tombol close/esc tidak di-bind; untuk keluar gunakan tombol close window)

## Penyesuaian
- Ubah konstanta di bagian atas `main.py` seperti `WIDTH`, `HEIGHT`, `PADDLE_SPEED`, `AI_SPEED`, `BALL_SPEED`, atau `MAX_SPIN` untuk menyesuaikan gameplay.

## Lisensi
MIT
