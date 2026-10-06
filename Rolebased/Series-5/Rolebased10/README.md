# Mini Chess Engine (Pygame + Unicode)

Engine catur mini yang dapat dimainkan, menggunakan Pygame dan karakter Unicode untuk merender bidak—tanpa aset gambar eksternal.

## Fitur
- Representasi papan dan aturan gerak dipisah (`Board` dan `Rules`).
- Klik untuk pilih, klik untuk jalan; sorot petak terpilih dan hint langkah.
- AI sederhana: evaluasi material (P=1, N/B=3, R=5, Q=9) dan prioritas makan “gratis”.
- Promosi otomatis menjadi Ratu (Queen).
- Status permainan: giliran, skakmat, dan stalemate.

Catatan: Rokade dan en passant tidak diimplementasikan (sengaja untuk kesederhanaan).

## Instalasi
Pastikan Python 3.8+ terpasang.

```bash
pip install -r requirements.txt
```

## Menjalankan
Di direktori proyek yang sama:

```bash
python chess_mini.py
```

## Kontrol
- Klik kiri: pilih bidak; klik lagi pada petak tujuan untuk bergerak.
- Putih = Anda (manusia), Hitam = AI.
- Tekan `R` untuk reset papan.

## Struktur Kode
- `chess_mini.py`: Seluruh implementasi.
  - `Board`: menyimpan state papan, giliran, utilitas terapkan langkah.
  - `Rules`: generator langkah pseudo-legal per bidak dan filter legal (tidak meninggalkan raja dalam cek).
  - AI: fungsi `ai_choose_move()` dan `evaluate_material()`.
  - Rendering: Pygame menggambar papan, bidak (Unicode), sorotan, dan panel status.

## Lisensi
MIT (opsional/ubah sesuai kebutuhan).
