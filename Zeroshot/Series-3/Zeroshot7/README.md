# Pacman Klasik - Python + Pygame

Game Pacman sederhana dengan ukuran layar 800x600 (grid 40x30, tile 20px) menggunakan Pygame.

## Fitur
- Maze 2D hardcoded menggunakan tile:
  - `1` = dinding
  - `0` = jalur kosong
  - `2` = pelet (dot)
  - `3` = power-pellet
- Pacman dikontrol dengan tombol panah, tidak menembus dinding.
- 4 Hantu dengan AI sederhana:
  - Mengejar Pacman (greedy) saat normal.
  - Menjadi rentan (warna cyan) saat Pacman mengambil power-pellet.
  - Jika tertangkap saat rentan, hantu menjadi "eaten" dan kembali ke markas.
- Skor, nyawa, kondisi menang (habis semua pelet) dan kalah (nyawa habis).

## Persyaratan
- Python 3.8+
- Pygame (lihat `requirements.txt`)

## Instalasi
Di PowerShell (Windows):

```
python -m pip install -r requirements.txt
```

Jika `python` tidak dikenali, coba:

```
py -m pip install -r requirements.txt
```

## Menjalankan

```
python main.py
```

Atau:

```
py main.py
```

## Kontrol
- Panah Atas/Bawah/Kiri/Kanan: Gerak Pacman
- R: Restart (saat Game Over atau Win)
- ESC: Keluar

## Struktur File
- `main.py` — kode utama game (loop, entitas, AI, rendering)
- `requirements.txt` — daftar dependensi
- `README.md` — panduan ini

Selamat bermain!
