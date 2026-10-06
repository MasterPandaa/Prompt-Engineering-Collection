# Tetris (Python + Pygame)

Tetris OOP dengan `Piece` dan `Board`, sudah termasuk fitur ghost piece, line clearing efisien, preview next piece, skor, level, dan kontrol yang nyaman.

## Persyaratan
- Python 3.8+
- Pygame (lihat `requirements.txt`)

## Instalasi (Disarankan Virtual Environment)
Di PowerShell (Windows):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Jika aktivasi venv diblokir kebijakan eksekusi, jalankan PowerShell sebagai Administrator lalu:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```
Kemudian ulangi aktivasi venv.

## Menjalankan Game
Setelah dependensi terpasang:

```powershell
python tetris.py
```

## Kontrol
- Kiri/Kanan atau A/D: Gerak horizontal
- Atas/W/X: Rotasi searah jarum jam
- Z: Rotasi berlawanan jarum jam
- Bawah/S: Soft drop
- Spasi: Hard drop
- Enter/Spasi: Restart saat Game Over
- Esc: Keluar

## Struktur Kode
- `tetris.py`
  - `class Piece`: bentuk, warna, posisi, rotasi (dengan wall kicks sederhana)
  - `class Board`: grid, tabrakan, lock piece, line clearing efisien, ghost piece, UI dasar
  - `class Game`: loop utama, input, gravitasi, skor/level, spawn piece (7-bag)
- `requirements.txt`: dependensi Pygame

## Catatan
- Ghost piece ditampilkan semi-transparan.
- Line clearing menggunakan filter list efisien, meminimalkan operasi berat per frame.

Selamat bermain! 🎮
