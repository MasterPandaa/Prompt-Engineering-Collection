# Pygame Chess (Text Pieces)

Game catur sederhana berbasis Pygame menggunakan teks (huruf) untuk merepresentasikan bidak.

## Fitur
- Representasi papan menggunakan huruf (huruf besar = putih, huruf kecil = hitam, '.' = kosong)
- Logika gerakan dasar untuk semua bidak: P, N, B, R, Q, K
- Validasi sederhana: tidak bisa memakan bidak sendiri
- Promosi pion otomatis menjadi menteri (Q)
- AI sederhana untuk hitam (greedy, memilih langkah yang meminimalkan evaluasi)
- Tampilan highlight seleksi dan titik tujuan langkah yang valid

## Instalasi

1. Pastikan Python 3.9+ sudah terpasang.
2. Install dependensi:

```bash
pip install -r requirements.txt
```

## Menjalankan Game

```bash
python chess_game.py
```

- Anda bermain sebagai putih. Klik kiri untuk memilih bidak putih, lalu klik petak tujuan yang valid.
- Tekan ESC untuk keluar.

## Catatan
- Tidak ada aturan skak, skakmat, en passant, ataupun rokade pada versi sederhana ini.
- Permainan berakhir ketika raja salah satu pihak hilang dari papan atau ketika pihak yang akan jalan tidak memiliki langkah (stalemate sederhana).
