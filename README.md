# Pygame Chess (Text Pieces)

Game catur sederhana menggunakan Pygame dengan representasi bidak sebagai huruf (teks). Putih dimainkan oleh manusia, Hitam oleh AI greedy (minimax kedalaman 1 setara penilaian material).

## Fitur
- Representasi papan berbasis array 8x8 dengan huruf: huruf besar = putih, huruf kecil = hitam, `.` = kosong.
- Gerakan dasar semua bidak: Pion, Kuda, Gajah, Benteng, Ratu, Raja.
- Validasi dasar: tidak bisa menabrak bidak sendiri; slider berhenti saat menabrak.
- Promosi otomatis pion menjadi Ratu saat mencapai baris terakhir.
- Rendering bidak sebagai huruf menggunakan `pygame.font`.
- AI sederhana (greedy): memilih langkah yang memaksimalkan (untuk putih) atau meminimalkan (untuk hitam) evaluasi material pada kedalaman 1.

Catatan keterbatasan (sengaja disederhanakan agar mudah dipelajari):
- Tidak ada en passant.
- Tidak ada rokade (castling).
- Tidak ada deteksi skak, skakmat, atau stalemate formal (namun jika AI tidak punya langkah, akan diberitahu di status).

## Persyaratan
- Python 3.9+ (disarankan)
- Pygame

## Instalasi
Di terminal/powershell, dari folder proyek ini:

```bash
python -m pip install -r requirements.txt
```

Jika instalasi via `requirements.txt` bermasalah, bisa langsung:

```bash
python -m pip install pygame
```

## Menjalankan
Jalankan file utama:

```bash
python chess_game.py
```

## Cara Bermain
- Anda bermain sebagai Putih, giliran pertama.
- Klik kiri pada bidak putih untuk memilih, maka petak tujuan legal akan ditandai (hijau untuk langkah biasa, merah untuk makan).
- Klik kiri pada petak tujuan untuk melakukan langkah.
- Setelah Anda melangkah, AI (Hitam) akan otomatis melangkah.

## Struktur File
- `chess_game.py` — kode utama (logika papan, gerakan, rendering, input, AI).
- `requirements.txt` — dependensi Python.

## Kustomisasi
- Ubah ukuran papan atau warna di konstanta bagian atas `chess_game.py` (misal `WIDTH`, `HEIGHT`, `LIGHT_COLOR`, `DARK_COLOR`).
- Ubah nilai material di `PIECE_VALUES` untuk mempengaruhi preferensi AI.

## Lisensi
Contoh edukasi. Gunakan dan modifikasi bebas.
