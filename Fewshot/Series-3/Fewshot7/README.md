# Pacman Pygame (Contoh Lengkap)

Game Pacman sederhana berbasis Pygame yang merender maze dari grid 2D, menggerakkan Pacman dengan tombol panah, dua hantu AI (bergerak acak/menjauh saat frightened), serta logika collision dan power-up.

## Fitur
- Render maze berdasarkan list 2D (`MAZE_LAYOUT`) dengan kode: 1 = dinding, 0 = kosong, 2 = pelet kecil, 3 = power-pellet.
- Gerak Pacman menggunakan tombol panah; memakan pelet dan power-pellet.
- Dua hantu AI bergerak acak di jalur yang tersedia. Saat Pacman power-up, hantu melambat dan cenderung menjauh.
- Collision Pacman vs hantu: saat power-up Pacman bisa memakan hantu; jika tidak, Pacman kehilangan nyawa dan respawn.
- HUD: skor, nyawa, sisa waktu power-up, status Game Over/Menang, dan reset (R).

## Persyaratan
- Python 3.9+ (disarankan)
- Pygame

Instalasi dependencies:
```
python -m pip install -r requirements.txt
```

## Cara Menjalankan
Di folder proyek ini jalankan:
```
python main.py
```

Kontrol:
- Panah Atas/Bawah/Kiri/Kanan: gerakkan Pacman
- Esc: keluar
- R: reset saat Game Over atau Menang

## Struktur Grid Maze
`MAZE_LAYOUT` berada di `main.py`. Nilai tile:
- 1: Dinding
- 0: Kosong
- 2: Pelet
- 3: Power-Pellet

Ubah layout sesuai kebutuhan. Ukuran tile (`TILE_SIZE`) dan kecepatan (`PACMAN_SPEED`, `GHOST_SPEED`) juga dapat diubah di bagian konfigurasi `main.py`.

## Catatan Teknis
- Pergerakan grid-based: pergantian arah hanya terjadi saat Pacman berada di pusat sel.
- Timer power-up default 7 detik; dapat disesuaikan via `POWER_DURATION`.
- Kondisi Menang: semua pelet habis.
- Kondisi Game Over: nyawa <= 0.
