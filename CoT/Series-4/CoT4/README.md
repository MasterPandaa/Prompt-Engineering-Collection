# Tetris (Pygame)

Game Tetris sederhana dibangun dengan Pygame.

## Fitur
- Grid 10x20 dengan ukuran blok 30px.
- 7 bentuk Tetris klasik (I, O, T, S, Z, J, L).
- Rotasi dengan "wall kick" sederhana.
- Soft drop (tombol panah bawah), hard drop (spasi).
- Scoring sederhana berdasarkan jumlah baris yang dibersihkan per sekali jatuh.

## Kontrol
- Panah Kiri/Kanan: Gerak horizontal.
- Panah Atas: Rotasi searah jarum jam.
- Panah Bawah: Soft drop.
- Spasi: Hard drop.
- Tutup jendela: Keluar.

## Cara Menjalankan (Windows)
1. Buat dan aktifkan virtual environment (opsional tapi direkomendasikan).
2. Install dependensi.
3. Jalankan game.

### Perintah contoh
```powershell
# (Opsional) buat virtual env
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependensi
pip install -r requirements.txt

# Jalankan game
python tetris.py
```

## Struktur Kode
- `tetris.py`: Implementasi lengkap game.
  - `Piece` class menyimpan posisi, bentuk, rotasi, warna.
  - `create_grid()`, `valid_space()`, `convert_shape_format()` untuk logika grid/tabrakan.
  - `clear_rows()` untuk deteksi dan penghapusan baris penuh serta penurunan blok.
  - `draw_window()`, `draw_next_shape()` untuk rendering.
  - `main()` berisi game loop.

## Catatan
- Jika font default `segoeui` tidak tersedia, Pygame akan fallback ke font default sistem.
- Ukuran window: 500x700 (playfield + panel samping).
