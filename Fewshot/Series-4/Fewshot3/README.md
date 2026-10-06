# Tetris (Pygame)

Implementasi penuh game Tetris menggunakan Pygame.

## Fitur
- 7 bentuk tetromino (I, O, T, S, Z, J, L) dengan rotasi.
- Grid 10x20.
- Deteksi tabrakan (dinding, dasar, dan bidak lain).
- Pembersihan baris penuh dan skor.
- Gravity, soft drop, hard drop, dan rotasi dengan simple wall-kick.

## Kontrol
- Panah Kiri/Kanan: Gerakkan bidak.
- Panah Bawah: Turunkan bidak lebih cepat (soft drop).
- Panah Atas: Rotasi bidak searah jarum jam.
- Spasi: Hard drop.
- Esc: Keluar.

## Persyaratan
- Python 3.9+ disarankan.
- Pygame (lihat `requirements.txt`).

## Cara Menjalankan (Windows)
1. Opsional (disarankan): buat virtual environment
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
2. Instal dependensi
   ```powershell
   python -m pip install -r requirements.txt
   ```
3. Jalankan game
   ```powershell
   python tetris.py
   ```

## Struktur File
- `tetris.py` — kode utama game.
- `requirements.txt` — dependensi Python.
- `README.md` — panduan ini.

Selamat bermain!
