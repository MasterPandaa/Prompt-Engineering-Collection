# Tetris (Pygame)

Implementasi lengkap game Tetris menggunakan Pygame.

Fitur:
- 7 tetromino (I, O, S, Z, J, L, T) beserta rotasinya.
- Grid 10x20, ukuran blok 30px.
- Deteksi tabrakan dinding, dasar, dan bidak terkunci.
- Pembersihan baris penuh dengan pergeseran blok di atasnya.
- Skor dan level (kecepatan meningkat tiap 10 baris).
- Kontrol: Panah Kiri/Kanan (gerak), Panah Atas (rotasi), Panah Bawah (soft drop), Spasi (hard drop), R (restart), ESC (keluar).

## Persyaratan
- Python 3.8+
- Pygame

## Instalasi

Di terminal/powershell, jalankan perintah berikut di folder proyek ini:

```
python -m pip install -r requirements.txt
```

## Menjalankan Game

```
python tetris.py
```

Jika jendela tidak muncul atau terjadi error terkait display, pastikan Pygame terpasang dan Anda menjalankannya di lingkungan desktop (bukan server headless).

## Struktur Berkas
- `tetris.py`: kode utama game.
- `requirements.txt`: daftar dependensi (pygame).
- `README.md`: panduan ini.
