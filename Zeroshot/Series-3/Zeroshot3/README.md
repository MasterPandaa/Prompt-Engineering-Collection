# Pacman (Python + Pygame)

Klasik Pacman game yang dibuat dengan Python dan Pygame.

## Spesifikasi
- Resolusi layar: 800x600
- Maze di-hardcode menggunakan angka:
  - `1` = dinding
  - `0` = jalur kosong (tanpa pelet)
  - `2` = pelet (dot)
  - `3` = power-pellet
- Pacman dikendalikan tombol panah dan tidak bisa menembus dinding.
- 4 hantu dengan AI sederhana (pilih arah di persimpangan, mendekati Pacman).
- Power mode: hantu menjadi rentan sementara waktu dan dapat dimakan.
- Skor dan nyawa ditampilkan, menang jika semua pelet termakan.

## Persiapan
1. Buat virtual environment (opsional namun direkomendasikan).
2. Install dependensi:

```
pip install -r requirements.txt
```

## Menjalankan Game
```
python main.py
```

Kontrol:
- Panah kiri/kanan/atas/bawah untuk bergerak.
- R untuk restart setelah Game Over / Menang.
- Esc untuk keluar.

## Catatan
- Maze dan parameter (kecepatan, durasi power-up, skor) dapat diubah di bagian konstanta dalam `main.py`.
