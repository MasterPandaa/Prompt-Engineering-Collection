# Tetris (Pygame)

Game Tetris sederhana yang dibuat dengan Pygame.

## Fitur

- 7 tetromino (I, O, T, S, Z, J, L) lengkap dengan rotasi.
- Grid 10x20 untuk gameplay.
- Deteksi tabrakan (dinding, dasar, dan bidak terkunci).
- Pembersihan baris penuh dan sistem skor.
- Soft drop (↓), hard drop (Space), dan rotasi (↑).
- Menu dan layar Game Over sederhana.

## Persyaratan

- Python 3.8+
- Pygame (lihat `requirements.txt`)

## Instalasi

Di PowerShell (Windows):

```powershell
# (Opsional) Buat dan aktifkan virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependensi
pip install -r requirements.txt
```

## Menjalankan Game

```powershell
python main.py
```

## Kontrol

- Panah Kiri/Kanan: Geser bidak.
- Panah Bawah: Turunkan lebih cepat (soft drop).
- Panah Atas: Rotasi searah jarum jam.
- Spasi: Hard drop.
- R: Restart saat bermain / setelah Game Over.
- Esc atau Q: Keluar dari game saat layar Game Over.

## Struktur Utama Kode

- `main.py`
  - `Piece`: representasi sebuah tetromino, termasuk rotasi dan posisi blok.
  - `create_grid()`: membangun grid 10x20 berdasarkan posisi terkunci.
  - `valid_space()`: validasi tabrakan dinding, dasar, dan blok.
  - `clear_rows()`: bersihkan baris penuh dan jatuhkan blok di atasnya.
  - `try_rotate_with_kicks()`: rotasi dengan "wall kick" sederhana.
  - `main()`: loop permainan utama.
  - `main_menu()`: layar menu dan entry point.

## Catatan

- Kecepatan jatuh meningkat sedikit demi sedikit seiring jumlah baris yang dibersihkan.
- Skor per baris: 1=100, 2=300, 3=500, 4=800.
