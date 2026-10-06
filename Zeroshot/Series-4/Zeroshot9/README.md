# Tetris (Python + Pygame)

Implementasi game Tetris klasik menggunakan Python dan Pygame.

## Fitur
- Papan 10 kolom x 20 baris, ukuran blok 30px.
- 7 Tetromino (I, O, T, S, Z, J, L) dengan warna berbeda.
- Kontrol:
  - Panah Kiri/Kanan: geser bidak.
  - Panah Bawah: soft drop (mempercepat jatuh). Tahan untuk mempercepat, lepaskan untuk kembali normal.
  - Panah Atas: rotasi searah jarum jam (dengan wall-kick sederhana).
  - Spasi: hard drop (jatuh ke posisi terendah dan terkunci).
  - ESC: keluar.
- Mekanisme:
  - Bidak spawn di atas, posisi tengah papan.
  - Lock ketika menyentuh dasar atau bidak lain.
  - Line clear: baris penuh dihapus, blok di atas turun.
  - Skor:
    - Soft drop: +1 per langkah.
    - Hard drop: +2 per langkah.
    - Clear 1/2/3/4 garis: +100/300/500/800.
- Game Over jika bidak baru tidak bisa spawn (papan penuh). Layar Game Over: tekan `R` untuk restart, `ESC` untuk keluar.

## Persyaratan
- Python 3.8+
- Pygame (lihat `requirements.txt`)

## Instalasi
Di terminal/PowerShell, jalankan perintah dari direktori proyek ini:

```powershell
pip install -r requirements.txt
```

Opsional (disarankan): gunakan virtual environment.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Menjalankan

```powershell
python main.py
```

Jika jendela tidak muncul atau ada error, pastikan Pygame telah terpasang dan driver grafis up-to-date.

## Struktur File
- `main.py` — kode utama permainan.
- `requirements.txt` — dependensi Python.
- `README.md` — dokumentasi dan instruksi.
