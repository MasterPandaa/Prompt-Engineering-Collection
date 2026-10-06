# Catur Pygame (Tanpa Gambar Eksternal)

Proyek kecil ini mengimplementasikan game catur standar menggunakan Python dan Pygame, tanpa file gambar eksternal. Bidak dirender menggunakan Unicode chess (contoh: ♔ ♕ ♖) dengan fallback bentuk geometri sederhana jika font tidak tersedia.

## Fitur
- Papan 8x8 dengan warna selang-seling.
- Bidak: Pawn, Rook, Knight, Bishop, Queen, King.
- Aturan gerak dasar dan giliran (Putih lalu Hitam).
- Deteksi skak (check) dasar.
- Promosi pion otomatis menjadi Queen saat mencapai baris terakhir.
- AI Hitam sederhana (memilih langkah legal acak, memprioritaskan tangkap jika ada).
- Interaksi mouse: klik bidak putih, lalu klik petak tujuan.
- Tanpa gambar eksternal (Unicode/fallback bentuk sederhana).

Catatan: Untuk kesederhanaan, en passant dan castling tidak diimplementasikan.

## Persyaratan
- Python 3.9+
- Pygame

## Instalasi
Di terminal/PowerShell, jalankan:

```bash
python -m pip install -r requirements.txt
```

Jika Anda ingin memasang Pygame secara manual:

```bash
python -m pip install pygame
```

## Menjalankan

```bash
python main.py
```

Jika font Unicode catur tidak tersedia di sistem Anda, aplikasi akan otomatis menampilkan fallback bentuk sederhana (lingkaran) untuk bidak.

## Kontrol
- Klik kiri: pilih bidak putih dan klik lagi pada petak tujuan yang di-highlight.
- Tombol `R`: reset permainan ke posisi awal.
- `Esc`: keluar.

## Struktur Proyek
- `main.py`: implementasi lengkap game.
- `requirements.txt`: daftar dependensi.
- `README.md`: berkas ini.

## Lisensi
MIT
