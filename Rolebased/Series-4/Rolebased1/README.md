# Tetris OOP (Python + Pygame)

Klona Tetris yang ditulis dengan pendekatan OOP menggunakan Python dan Pygame. Termasuk fitur ghost piece, rotasi dengan wall-kicks sederhana, line clearing efisien, dan panel status.

## Fitur
- OOP: `Piece` dan `Board` mengelola bentuk, state papan, validasi, dan clearing.
- Ghost piece: bayangan posisi jatuh akhir bidak secara real-time.
- Wall-kick sederhana saat rotasi.
- Sistem skor dan level, kecepatan jatuh bertambah seiring level.
- Preview 3 bidak berikutnya (bag randomizer 7-bag).

## Persyaratan
- Python 3.8+
- Pygame (lihat `requirements.txt`).

## Instalasi (Windows PowerShell)
```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Menjalankan
```powershell
python .\main.py
```

## Kontrol
- Left / Right: Geser bidak
- Down: Soft drop (tambahan skor kecil)
- Up / Z: Rotasi searah jarum jam / berlawanan
- Space: Hard drop
- P: Pause
- R: Restart
- Esc: Keluar

## Catatan Teknis
- Grid: 10x20, ukuran blok 32px.
- Clearing: memfilter baris penuh dan menyisipkan baris kosong di atas (O(H*W)).
- Ghost piece dirender semi-transparan di dasar valid.
- Rotasi menggunakan offset wall-kick sederhana `(0,0), (-1,0), (1,0), (0,-1), (-2,0), (2,0)`.

## Struktur File
- `main.py` — implementasi game loop, kelas, dan rendering.
- `requirements.txt` — dependensi Pygame.
- `README.md` — petunjuk dan dokumentasi.

Selamat bermain!
