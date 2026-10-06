# Pygame Chess (Unicode)

Game catur sederhana menggunakan Python dan Pygame.

- Papan 8x8 dengan warna selang-seling.
- Bidak ditampilkan dengan simbol Unicode (tanpa file gambar).
- Aturan gerak dasar semua bidak, giliran jalan, deteksi skak (check) dasar.
- AI Hitam: memilih langkah legal dengan preferensi tangkap sederhana.
- Interaksi: klik bidak putih, lalu klik petak tujuan. Sorotan petak legal akan muncul.
- Promosi pion otomatis menjadi menteri (Queen).

## Prasyarat

- Python 3.8+
- Pygame

Instal dependensi:

```bash
pip install -r requirements.txt
```

## Menjalankan

```bash
python chess_pygame.py
```

## Catatan

- Tidak ada en passant atau rokade untuk menyederhanakan implementasi.
- Deteksi skakmat/patut seri (stalemate) dasar: jika pihak yang akan jalan tidak punya langkah legal, dinilai skakmat bila sedang skak, selain itu stalemate.
- Jika font sistem tidak memiliki glyph Unicode catur, akan fallback menggambar bentuk lingkaran beserta huruf bidak.
