# Tetris (Python + Pygame)

Game Tetris klasik yang bisa langsung dijalankan dengan Python dan Pygame.

## Spesifikasi
- Grid 10 kolom x 20 baris
- Ukuran blok 30 piksel
- 7 Tetromino: I, O, T, S, Z, J, L (warna unik)
- Kontrol:
  - Panah Kiri/Kanan: geser bidak
  - Panah Bawah: soft drop (lebih cepat)
  - Panah Atas: rotasi
  - Space: hard drop (langsung jatuh ke dasar)
- Skor line clear: 1=100, 2=300, 3=500, 4=800
- Game Over saat bidak baru bertabrakan di atas

## Persyaratan
- Python 3.8+
- Pygame

## Instalasi
Di PowerShell/Command Prompt pada folder proyek:

```powershell
python -m pip install -r requirements.txt
```

## Menjalankan
```powershell
python tetris.py
```

## Catatan
- Kecepatan jatuh bertambah perlahan seiring waktu.
- Terdapat preview "Next" piece di sidebar kanan beserta skor dan high score sesi.
