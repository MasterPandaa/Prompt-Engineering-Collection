# Pacman (Pygame)

Implementasi klona Pacman sederhana menggunakan Python dan Pygame dengan pendekatan OOP.

## Fitur
- Kelas terpisah: `Game`, `Maze`, `Player`, `Ghost`.
- Maze dirender dari layout 2D hardcoded.
- Pellets dan power-pellets; power-pellet membuat hantu menjadi `vulnerable` sementara waktu.
- 2 AI hantu:
  - `Chaser`: mengejar pemain (heuristik jarak grid / BFS sederhana).
  - `Random`: bergerak acak, menghindari balik arah kecuali buntu.
- Skor, nyawa, game over, restart tekan `R`.

## Persyaratan
- Python 3.9+
- Pygame

Install dependency:

```bash
pip install -r requirements.txt
```

## Menjalankan

```bash
python pacman.py
```

Kontrol:
- Panah (atau WASD) untuk bergerak.
- R untuk restart saat Game Over.
- ESC untuk keluar.

## Struktur OOP Singkat
- `Maze`: memuat layout, posisi dinding, pellets, power-pellets, spawn player & hantu.
- `Player`: input, gerak grid-based, collision, makan pellets/power.
- `Ghost`: state `normal`/`vulnerable`, AI chaser / random.
- `Game`: loop utama, skor, nyawa, render, reset.

## Catatan
- Ini adalah versi edukasi dan tidak mereplikasi semua detail orisinal Pac-Man.
