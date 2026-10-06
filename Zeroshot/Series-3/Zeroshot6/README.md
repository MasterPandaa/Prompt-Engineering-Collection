# Pacman (Python + Pygame)

Game Pacman klasik sederhana menggunakan Python dan Pygame.

Spesifikasi:
- Layar: 800x600 piksel.
- Maze: Layout 2D hardcoded; `1` untuk dinding, `0` untuk jalur kosong, `2` untuk pelet, `3` untuk power-pellet.
- Pacman: Dikontrol tombol arah; tidak dapat menembus dinding.
- Pelet: Dimakan Pacman untuk skor.
- Power-Pellets: Membuat hantu rentan sementara; saat rentan dan tertangkap Pacman, hantu "eaten" dan kembali ke markas.
- Hantu: 3-4 hantu dengan AI sederhana (bias mendekati Pacman di persimpangan, random saat frightened, menuju rumah saat eaten).
- HUD: Skor dan nyawa.
- Kondisi: Menang jika semua pelet habis, kalah jika nyawa habis.

## Persyaratan
- Python 3.8+
- Pygame

## Instalasi
Di Windows, jalankan perintah berikut di folder proyek ini:

```powershell
py -m pip install -r requirements.txt
```

Jika `py` tidak tersedia, gunakan:

```powershell
python -m pip install -r requirements.txt
```

## Menjalankan Game
Masih di folder proyek, jalankan:

```powershell
py main.py
```

Atau:

```powershell
python main.py
```

Kontrol:
- Panah Atas/Bawah/Kiri/Kanan untuk bergerak.
- ESC untuk keluar.
- Saat Game Over/Win: Tekan `R` untuk restart.

## Struktur Kode
- `main.py`: Seluruh implementasi game, termasuk:
  - `load_maze()`: Membangun maze 32x24 tile untuk layar 800x600 (tiap tile 25px).
  - `Entity`, `Pacman`, `Ghost`: Logika gerak, state, dan render.
  - `Game`: Loop utama, update, render, HUD, kondisi menang/kalah.

## Catatan
- Kecepatan hantu berubah berdasarkan state (normal, frightened, eaten).
- Power-Pellet berlangsung sekitar 8 detik; hantu berkedip saat hampir habis.
- Restart (R) mengatur ulang maze, skor, dan nyawa.
