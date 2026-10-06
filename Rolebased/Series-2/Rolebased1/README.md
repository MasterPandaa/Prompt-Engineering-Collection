# Snake Game (Pygame)

Implementasi game Snake klasik yang bersih, efisien, dan mudah dipelihara menggunakan Pygame.

## Fitur

- Layar 600x400 (grid 30x20 dengan ukuran sel 20px)
- Struktur berbasis kelas: `Snake` dan `Food`
- Kontrol responsif menggunakan tombol panah, dengan guard untuk mencegah berbalik arah
- Mekanisme pertumbuhan ular yang akurat
- Penempatan makanan acak yang efisien (menghindari tubuh ular)
- Deteksi tabrakan dinding dan tubuh sendiri (game reset)
- Tampilan skor

## Menjalankan

1. Buat virtual environment (opsional namun direkomendasikan)
2. Instal dependensi:

```
pip install -r requirements.txt
```

3. Jalankan game:

```
python main.py
```

## Kontrol

- Panah Kiri/Kanan/Atas/Bawah untuk mengubah arah
- Escape untuk keluar

## Catatan Teknis

- Kecepatan gerak diatur dengan event timer (`pygame.USEREVENT`) agar input tetap responsif tanpa mengandalkan `Clock.tick` semata.
- Grid memastikan gerakan ular presisi per sel (20px) dan memudahkan deteksi tabrakan serta penempatan makanan.
- Reset game dilakukan otomatis saat tabrakan, tanpa layar terpisah, agar loop tetap sederhana.
