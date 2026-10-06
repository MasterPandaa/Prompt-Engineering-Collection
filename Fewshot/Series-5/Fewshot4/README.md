# Catur Pygame (Huruf)

Game catur sederhana menggunakan Pygame dengan representasi bidak sebagai huruf:
- Huruf besar = Putih
- Huruf kecil = Hitam
- '.' (titik) = Petak kosong

Fitur:
- Gerakan dasar seluruh bidak (tanpa en passant, rokade, atau deteksi skak-mat penuh)
- Promosi pion otomatis menjadi ratu
- AI sederhana (greedy) untuk pihak Hitam
- Render teks menggunakan `pygame.font`

## Persyaratan

- Python 3.9+
- Pygame

Install dependensi:

```bash
pip install -r requirements.txt
```

## Menjalankan Game

```bash
python main.py
```

Kontrol:
- Klik kiri untuk memilih bidak putih dan klik lagi pada petak tujuan yang disorot.
- Tekan `R` untuk reset posisi awal.
- Tekan `ESC` untuk keluar.

## Catatan
- Validasi yang diimplementasikan adalah validasi dasar: tidak bisa menabrak bidak sendiri dan pergerakan sesuai tipe bidak.
- Fitur-fitur lanjutan seperti en passant, rokade, deteksi skak dan skak-mat tidak termasuk untuk menjaga kesederhanaan.
