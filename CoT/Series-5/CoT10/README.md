# Pygame Chess vs AI (Simple)

Game catur sederhana melawan AI berbasis Pygame. Tidak membutuhkan aset gambar eksternal; bidak divisualisasikan menggunakan Unicode.

## Fitur
- Representasi papan 8x8 menggunakan list 2D berisi string bidak (`wP`, `bK`, dll.).
- Generator langkah pseudo-legal: pion (termasuk dua langkah awal), kuda, gajah, benteng, menteri, raja.
- Promosi pion otomatis menjadi menteri.
- Validasi turn: hanya bisa gerakkan bidak milik pemain saat gilirannya.
- AI sederhana: memilih capture bernilai tertinggi, jika tidak ada memilih langkah acak.
- Input mouse: klik untuk memilih dan klik tujuan untuk memindahkan. Hint gerakan ditampilkan sebagai titik.

Catatan: Rokade, en passant, dan deteksi skak/cekmat tidak diimplementasikan untuk menjaga kesederhanaan.

## Kebutuhan
- Python 3.8+
- Pygame 2.5+

Install dependencies:

```bash
pip install -r requirements.txt
```

## Menjalankan

```bash
python pygame_chess_ai.py
```

- ESC untuk keluar.
- Pemain adalah putih, AI adalah hitam.

## Struktur File
- `pygame_chess_ai.py` — kode utama permainan.
- `requirements.txt` — dependensi.
- `README.md` — dokumen ini.
