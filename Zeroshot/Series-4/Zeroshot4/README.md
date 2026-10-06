# Tetris (Python + Pygame)

Implementasi Tetris klasik dengan papan 10x20, 7 tetromino, kontrol lengkap, skor, line clear, ghost piece, dan game over.

## Fitur
- Grid 10 x 20, ukuran blok 30 px.
- 7 Tetromino: I, O, T, S, Z, J, L dengan warna berbeda.
- Kontrol:
  - Panah Kiri/Kanan: gerak kiri/kanan
  - Panah Atas: rotasi
  - Panah Bawah: soft drop
  - Space: hard drop
  - R: restart
  - ESC: keluar
- Lock piece, line clearing, skor, ghost piece, preview next piece.

## Persyaratan
- Python 3.9+ (disarankan)
- Pygame (lihat `requirements.txt`)

## Cara Menjalankan (Windows / PowerShell)
1. (Opsional) Buat virtual environment dan aktifkan:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
2. Pasang dependensi:
   ```powershell
   pip install -r requirements.txt
   ```
3. Jalankan game:
   ```powershell
   python tetris.py
   ```

Jika jendela game tidak tampil atau terjadi error terkait video driver, pastikan Anda menjalankan perintah di lingkungan desktop (bukan sesi headless/SSH tanpa display).
