# Tetris (Pygame)

Implementasi game Tetris sederhana menggunakan Pygame. Mendukung rotasi, soft drop, hard drop, line clearing, skor, dan percepatan level.

## Fitur
- Grid 10x20 dengan ukuran blok 30px
- 7 bentuk Tetris (I, O, T, S, Z, J, L)
- Rotasi dengan wall-kick sederhana
- Soft drop, hard drop
- Line clear dan sistem skor (Tetris sederhana)
- Peningkatan kecepatan seiring jumlah baris yang dibersihkan

## Persyaratan
- Python 3.8+
- Pygame (lihat `requirements.txt`)

## Cara Menjalankan (Windows)
1. Buka terminal di folder proyek ini.
2. (Opsional) Buat virtual environment:
   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```
3. Instal dependensi:
   ```powershell
   pip install -r requirements.txt
   ```
4. Jalankan game:
   ```powershell
   python tetris.py
   ```

## Kontrol
- Panah Kiri/Kanan: Geser bidak
- Panah Atas: Rotasi
- Panah Bawah: Soft drop (turun 1 langkah)
- Spasi: Hard drop (turun sampai mentok)
- Esc: Keluar
- Enter (di menu): Mulai game

## Struktur File
- `tetris.py` — kode utama game
- `requirements.txt` — dependensi Python
- `README.md` — dokumen ini

## Catatan
- Jika window tidak muncul atau terjadi error terkait display, pastikan environment mendukung tampilan GUI dan driver grafis/SDL tersedia.
