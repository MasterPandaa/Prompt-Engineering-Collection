# Catur Pygame (Huruf)

Game catur sederhana menggunakan Pygame dengan representasi bidak berbasis huruf (kapital = Putih, kecil = Hitam). Pieces ditampilkan menggunakan `pygame.font` (teks), bukan sprite.

## Fitur
- Representasi papan berbasis list-of-lists.
- Gerakan valid dasar untuk semua bidak: Pion, Kuda, Gajah, Benteng, Ratu, Raja (tanpa rokade/en passant/cek-legal).
- Validasi: tidak bisa menabrak/menangkap bidak teman sendiri.
- AI sederhana (greedy depth-1): memilih langkah yang memaksimalkan material untuk dirinya.
- Click-to-move untuk pemain putih. AI bermain sebagai hitam.

## Instalasi

1. Buat virtualenv (opsional namun disarankan)
2. Install dependensi:

```bash
pip install -r requirements.txt
```

## Menjalankan

```bash
python main.py
```

Kontrol:
- Klik kiri untuk memilih bidak putih dan klik petak tujuan yang di-highlight.
- Tekan `R` untuk reset.

## Catatan
- Ini adalah implementasi minimal untuk tujuan pembelajaran. Belum termasuk aturan lanjutan: cek/cekmat, rokade, en passant, tiga kali pengulangan, 50-move rule, promosi ke selain ratu via UI, dsb.
