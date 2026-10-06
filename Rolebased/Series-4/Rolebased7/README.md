# Tetris (Python + Pygame)

Sebuah implementasi Tetris bergaya OOP menggunakan Python dan Pygame, mencakup:

- Kelas `Piece` untuk bentuk, warna, posisi, rotasi.
- Kelas `Board` untuk state papan, deteksi tabrakan, mengunci bidak, dan line clearing efisien.
- Fitur "ghost piece" untuk menampilkan bayangan posisi jatuh.
- Sistem skor, level, dan kontrol keyboard dasar.

## Menjalankan

1) Buat virtual environment (opsional tapi disarankan) dan install dependency:

```
pip install -r requirements.txt
```

2) Jalankan game:

```
python main.py
```

## Kontrol

- Left/Right: Geser bidak
- Up / Z: Rotasi searah / berlawanan jarum jam
- Down: Soft drop
- Space: Hard drop
- P: Pause
- R: Restart saat Game Over
- Esc: Keluar

## Catatan Teknis

- Line clearing dilakukan dengan satu pass untuk menghitung baris penuh dan membangun ulang grid, meminimalkan overhead.
- Ghost piece dihitung dengan menjatuhkan kopian bidak aktif sampai tabrakan berikutnya, kemudian digambar sebagai outline abu-abu.
- Rotasi menggunakan skema wall-kick sederhana (tidak 100% SRS) yang efektif untuk permainan kasual.
