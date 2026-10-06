# Tetris (Pygame)

Game Tetris sederhana menggunakan Pygame.

## Fitur
- Grid 10x20 dengan ukuran blok 32px
- 7 bentuk Tetris (S, Z, I, O, J, L, T)
- Rotasi dengan wall-kick sederhana
- Soft drop, hard drop, pause
- Skor dan level (kecepatan naik tiap 10 baris)
- Preview bidak berikutnya

## Persyaratan
- Python 3.9+
- Pygame 2.6+

## Instalasi
Di terminal/powershell, jalankan perintah berikut dari folder proyek ini:

```powershell
python -m pip install -r requirements.txt
```

Opsional: gunakan virtual environment (disarankan):
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Menjalankan Game
```powershell
python tetris.py
```

Kontrol:
- Panah Kiri/Kanan: Geser
- Panah Atas: Rotasi
- Panah Bawah: Turun cepat (soft drop)
- Spasi: Hard drop
- P: Pause
- Esc: Keluar

## Struktur File
- `tetris.py`: kode utama game
- `requirements.txt`: dependensi Python
- `README.md`: panduan ini

Selamat bermain!
