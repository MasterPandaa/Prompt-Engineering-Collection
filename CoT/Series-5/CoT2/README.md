# Catur Pygame: Manusia vs AI

Game catur sederhana menggunakan Pygame dengan lawan AI dasar. Tidak membutuhkan aset gambar eksternal: bidak dirender menggunakan karakter Unicode.

## Fitur
- Representasi papan 8x8 berbasis list 2D.
- Generator langkah legal (tanpa rokade dan en passant) termasuk:
  - Langkah pion 1/2 petak dari posisi awal.
  - Tangkap diagonal pion.
  - Promosi otomatis ke menteri (queen).
- Validasi skak: filter langkah sehingga raja sendiri tidak dibiarkan skak.
- AI sederhana: memilih langkah dengan nilai tangkapan tertinggi; jika tidak ada, memilih acak.
- Highlight kotak terpilih, langkah yang mungkin, langkah terakhir, dan raja yang sedang diserang.
- Deteksi akhir permainan: skakmat dan stalemate.

## Persyaratan
- Python 3.9+ direkomendasikan.
- Pygame.

Instalasi dependensi:

```bash
pip install -r requirements.txt
```

## Menjalankan

```bash
python chess_pygame.py
```

## Kontrol
- Klik kiri untuk memilih bidak Anda (Putih) dan klik lagi pada kotak tujuan yang di-highlight untuk bergerak.
- Tekan `R` untuk restart.
- Tekan `ESC` untuk keluar.

## Catatan
- Fitur yang sengaja tidak diimplementasi demi kesederhanaan: rokade (castling) dan en passant.
- Promosi selalu menjadi menteri (queen).
- Jika font default sistem Anda tidak menampilkan simbol catur, Anda masih dapat mengganti font pada bagian inisialisasi `piece_font` di `chess_pygame.py` ke font yang mendukung Unicode simbol catur.
