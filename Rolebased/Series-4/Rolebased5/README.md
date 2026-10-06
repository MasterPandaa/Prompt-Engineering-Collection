# Tetris (Python + Pygame)

Sebuah klona Tetris yang robust, efisien, dan mudah dipahami. Ditulis dengan pendekatan OOP menggunakan Python dan Pygame.

Fitur utama:
- OOP yang jelas: kelas `Piece` dan `Board` memisahkan tanggung jawab.
- Ghost piece (bayangan) yang menunjukkan posisi jatuh akhir.
- Deteksi tabrakan yang akurat dan line clearing efisien (kompaksi grid sekali operasi).
- Skor, level bertahap, dan soft/hard drop.

## Persyaratan
- Python 3.9+
- Pygame (lihat `requirements.txt`)

## Instalasi
Di terminal/powershell, dari direktori proyek ini:

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Menjalankan
```
python tetris.py
```

## Kontrol
- Panah Kiri/Kanan: Geser bidak ke kiri/kanan
- Panah Atas: Rotasi searah jarum jam
- Z: Rotasi berlawanan jarum jam
- Panah Bawah: Soft drop (lebih cepat, +1 skor per langkah)
- Spasi: Hard drop (langsung jatuh, +2 skor bonus)
- C: Restart cepat saat kapan pun
- ESC: Keluar

## Struktur Kode
- `tetris.py`
  - `class Piece`: menyimpan bentuk, rotasi, warna, posisi, utilitas `cells()` dan `rotated()`.
  - `class Board`: menyimpan grid, cek validitas, wall-kick sederhana saat rotasi, hard drop y, penguncian bidak, dan `clear_lines()` efisien.
  - `class Game`: loop utama, input, update gravitasi/lock delay, dan gambar layar (termasuk ghost piece).

## Catatan Teknis
- Line clearing efisien dengan memfilter baris penuh lalu menambahkan baris kosong di atas (O(Rows * Cols)).
- Ghost piece dihitung menggunakan `Board.hard_drop_y(piece)` lalu digambar semi-transparan.
- Drop interval menyesuaikan level (semakin tinggi level, semakin cepat). Level naik tiap 10 garis yang dibersihkan.

Selamat bermain!
