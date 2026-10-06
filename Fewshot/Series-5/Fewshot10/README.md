# Pygame Chess (Simple AI)

Game catur sederhana menggunakan Pygame. Bidak ditampilkan sebagai huruf (kapital = putih, kecil = hitam). AI menggunakan strategi greedy (kedalaman 1) berbasis skor material.

Fitur:
- Representasi papan 8x8 berbasis array huruf.
- Logika gerak lengkap: Pion, Kuda, Gajah, Benteng, Ratu, Raja.
- Validasi dasar: tidak bisa menabrak bidak sendiri, bidak "slider" (gajah/benteng/ratu) tidak menembus.
- Promosi pion otomatis ke Ratu ketika mencapai baris terakhir.
- UI Pygame sederhana: klik untuk pilih bidak putih, klik lagi untuk tujuan; highlight langkah valid.
- AI (hitam) bermain otomatis dengan greedy.

Catatan: Belum mendukung skak/skakmat, en passant, atau castling.

## Persiapan

1) Pastikan Python 3.8+ terpasang.
2) Buat virtual environment (opsional tapi direkomendasikan) dan install dependensi:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Menjalankan

```powershell
python chess_pygame.py
```

Kontrol:
- Klik kiri: pilih bidak putih lalu klik petak tujuan.
- Tombol `R`: reset papan.
- Tutup jendela untuk keluar.

## Struktur File
- `chess_pygame.py` — kode utama game.
- `requirements.txt` — dependensi Pygame.
- `README.md` — panduan ini.
