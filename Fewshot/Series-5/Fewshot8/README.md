# Simple Chess (Pygame, Text Pieces)

Game catur sederhana menggunakan Pygame, menampilkan bidak sebagai teks huruf (huruf besar = putih, huruf kecil = hitam) sesuai contoh representasi papan.

Fitur:
- Representasi papan berbasis array 2D huruf ('.' = kosong).
- Logika gerak lengkap: pion, kuda, gajah, benteng, menteri, raja (tanpa castling dan en passant untuk kesederhanaan).
- Validasi dasar: tidak menabrak kawan, batas papan, jalur bersih untuk bidak meluncur.
- AI sederhana (greedy/depth-1) yang memilih langkah terbaik berdasarkan evaluasi material.
- Render papan dan bidak dengan `pygame.font`.

## Cara Menjalankan

1. Buat virtual environment (opsional tapi direkomendasikan) dan install dependensi:

```bash
pip install -r requirements.txt
```

2. Jalankan game:

```bash
python chess_game.py
```

Kontrol:
- Klik kiri untuk memilih bidak putih dan klik lagi pada petak tujuan yang valid.
- Titik abu-abu = langkah non-tangkap; titik merah = langkah menangkap.
- ESC atau menutup jendela untuk keluar.

Catatan:
- Aturan catur disederhanakan: belum ada cek/cekmat validasi, castling, en passant, atau tiga kali pengulangan. Kemenangan ditentukan jika salah satu raja tertangkap atau pihak lawan tidak memiliki langkah (dianggap kalah, bukan remis). Anda dapat memperluas aturan sesuai kebutuhan.
