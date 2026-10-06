# Catur Pygame (Human vs AI Greedy)

Game catur sederhana menggunakan Pygame. Bidak dirender sebagai teks huruf (R, N, B, Q, K, P). Putih dikendalikan pemain, Hitam dikendalikan AI greedy berbasis evaluasi material.

## Fitur
- Representasi papan 8x8 menggunakan huruf (huruf besar = putih, kecil = hitam, `.` = kosong).
- Logika gerakan lengkap untuk Pawn, Knight, Bishop, Rook, Queen, King.
- Promosi pion otomatis ke Queen.
- Validasi dasar: tidak dapat bergerak ke petak berisi bidak sendiri.
- AI sederhana (greedy): memilih langkah yang memaksimalkan materi setelah satu langkah (kedalaman 1). 
- Rendering dengan text font Pygame.

## Persiapan

1. Buat dan aktifkan virtual environment (opsional tapi disarankan).
2. Install dependency:

```bash
pip install -r requirements.txt
```

## Menjalankan

```bash
python main.py
```

- Klik sebuah bidak putih untuk menyorot langkah legalnya, lalu klik petak tujuan untuk bergerak.
- Setelah Anda bergerak, AI hitam akan langsung merespons.

## Catatan & Batasan
- Belum mendukung skak, skakmat, remis, en passant, dan castling.
- Evaluasi AI hanya material sehingga tidak memahami taktik/posisi kompleks.
- Cocok sebagai dasar untuk pengembangan fitur catur yang lebih lengkap.
