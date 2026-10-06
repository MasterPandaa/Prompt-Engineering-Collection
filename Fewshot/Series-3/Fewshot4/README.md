# Pacman Pygame (Contoh Lengkap)

Proyek ini adalah implementasi sederhana game Pacman menggunakan Pygame. Fitur:

- Render maze berbasis grid (1=dinding, 0=jalur, 2=pelet, 3=power-pellet)
- Pacman bergerak dengan tombol panah dan memakan pelet/power-pellet
- Dua hantu AI bergerak acak di jalur yang tersedia (menghindari putar balik jika bisa)
- Logika tabrakan Pacman vs Hantu dan status power-up (hantu menjadi frightened, dapat dimakan)
- HUD skor, nyawa, status level selesai dan game over

## Struktur File

- `main.py` — Kode utama game
- `requirements.txt` — Dependensi Python

## Persyaratan

- Python 3.9+
- Pygame (lihat `requirements.txt`)

## Cara Menjalankan

1) (Opsional, disarankan) Buat dan aktifkan virtual environment.

Windows (PowerShell):
```
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2) Install dependensi:
```
pip install -r requirements.txt
```

3) Jalankan game:
```
python main.py
```

## Kontrol

- Panah Atas/Bawah/Kiri/Kanan: Gerakkan Pacman
- Enter: Saat level selesai atau game over, mulai ulang
- Tutup jendela untuk keluar

## Catatan Teknis

- Ukuran tile: 48px. Ukuran window menyesuaikan jumlah baris/kolom maze + area HUD.
- Kecepatan Pacman vs Hantu diatur dalam konstanta `PACMAN_SPEED` dan `GHOST_SPEED`.
- Durasi power-up diatur di `POWER_DURATION_MS`.
- Maze dan pelet menggunakan `maze_layout` dan `pellet_map` (duplikasi maze untuk state pelet yang termakan).

Selamat bermain!
