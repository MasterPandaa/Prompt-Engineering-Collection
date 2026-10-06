# Tetris (Pygame)

Game Tetris sederhana menggunakan Pygame.

## Persiapan

1) Buat virtual environment (opsional tapi disarankan)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2) Install dependensi

```powershell
python -m pip install -r requirements.txt
```

## Menjalankan

```powershell
python tetris.py
```

## Kontrol

- Left/Right: Gerak kiri/kanan
- Up atau X: Rotasi searah jarum jam
- Z: Rotasi berlawanan jarum jam
- Down: Soft drop
- Space: Hard drop (langsung jatuh)
- P: Pause
- R: Restart (saat Game Over)
- ESC: Keluar

## Catatan Teknis

- Grid: 20x10, warna `BLACK` untuk sel kosong.
- Bidak aktif diwakili oleh `Piece` yang menyimpan bentuk, rotasi, posisi, dan warna.
- Rotasi memakai pola rotasi yang di-hardcode untuk tiap tetromino. Wall kick sederhana dicoba dengan offset ±1/±2 saat rotasi.
- Line clear men-scan dari bawah ke atas, menghapus baris penuh, dan menurunkan baris di atasnya.
- Skor mengikuti pendekatan 40/100/300/1200 × level untuk 1–4 garis.
