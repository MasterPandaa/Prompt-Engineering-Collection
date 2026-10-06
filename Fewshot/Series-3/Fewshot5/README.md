# Pacman (Pygame)

Game Pacman sederhana menggunakan Pygame.

## Fitur
- Render maze berbasis grid dari list 2D.
- Pacman bergerak dengan tombol panah, memakan pelet (2) dan power-pellet (3).
- 2 hantu AI dengan pergerakan acak di jalur yang tersedia.
- Logika tabrakan Pacman vs Hantu dan status power-up (ghost menjadi biru dan bisa dimakan dalam durasi tertentu).
- HUD skor dan indikator sisa waktu power.

## Persyaratan
- Python 3.8+
- Pygame (lihat `requirements.txt`)

## Instalasi
```bash
python -m pip install -r requirements.txt
```

## Menjalankan
```bash
python main.py
```

## Kontrol
- Panah Kiri/Kanan/Atas/Bawah: Gerak
- R: Restart
- ESC: Keluar

## Struktur
- `main.py`: Kode utama game (kelas `Maze`, `Pacman`, `Ghost`, dan loop game).
- `requirements.txt`: Dependensi.
- `README.md`: Dokumen ini.

## Kustomisasi Maze
Ganti nilai pada konstanta `MAZE_LAYOUT` di `main.py` dengan layout Anda sendiri. Contoh kecil:
```python
# 1 = Dinding, 0 = Jalur Kosong, 2 = Pelet Kecil, 3 = Power Pellet
maze_layout = [
    [1, 1, 1, 1, 1, 1, 1],
    [1, 2, 2, 3, 2, 2, 1],
    [1, 2, 1, 1, 1, 2, 1],
    [1, 2, 2, 2, 2, 2, 1],
    [1, 3, 1, 1, 1, 3, 1],
    [1, 2, 2, 2, 2, 2, 1],
    [1, 1, 1, 1, 1, 1, 1]
]
```
Pastikan ukuran layar dan `TILE_SIZE` masih sesuai. Secara default, `TILE_SIZE` dihitung otomatis dari ukuran layar dan dimensi maze.

## Catatan
- Kecepatan entitas diskalakan dari `TILE_SIZE` agar gameplay tetap proporsional di berbagai ukuran maze.
- Ghost menghindari berbalik arah kecuali buntu, sehingga terasa lebih natural.
