# Tetris (Pygame)

Implementasi game Tetris lengkap menggunakan Pygame.

## Fitur
- 7 tetromino: I, O, T, S, Z, J, L.
- Rotasi searah jarum jam dengan wall-kick sederhana.
- Grid permainan 10x20, ukuran blok 30px.
- Deteksi tabrakan (dinding, dasar, dan bidak terkunci).
- Pembersihan baris penuh dan perhitungan skor.
- Preview bidak berikutnya.
- Pause dan game over screen.

## Kontrol
- Left/Right: Geser kiri/kanan
- Up: Rotasi
- Down: Soft drop (turun satu langkah)
- Space: Hard drop (langsung kunci)
- P: Pause/Resume
- Esc: Keluar

## Persyaratan
- Python 3.8+
- Pygame (lihat `requirements.txt`)

## Instalasi (Windows)
1. (Opsional) Buat virtual environment:
   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
2. Instal dependensi:
   ```powershell
   py -m pip install -r requirements.txt
   ```

## Menjalankan
```powershell
py main.py
```

Jika jendela tidak muncul atau terjadi error terkait display/SDL, pastikan Python dan Pygame terpasang dengan benar serta driver/layanan grafis berjalan normal.

## Struktur Proyek
- `main.py` — Seluruh logika game.
- `requirements.txt` — Dependensi Python.
- `README.md` — Petunjuk penggunaan.
