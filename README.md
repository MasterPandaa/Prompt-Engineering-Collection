# Pygame Chess (Huruf)

Game catur sederhana menggunakan Pygame dengan representasi papan huruf.

- Bidak putih: huruf besar (R N B Q K P)
- Bidak hitam: huruf kecil (r n b q k p)
- Petak kosong: titik `.`

Fitur:
- Klik untuk memilih bidak putih dan klik petak tujuan untuk melangkah.
- Validasi langkah dasar untuk semua tipe bidak (pion, benteng, kuda, gajah, menteri, raja).
- Tidak bisa menabrak bidak sendiri; bidak geser (benteng/gajah/menteri) tidak bisa melompati.
- AI sederhana (hitam) dengan evaluasi greedy (minimax kedalaman 1).
- Promosi pion otomatis menjadi menteri ketika mencapai baris terakhir.
- Tanpa rokade, en passant, dan deteksi skak.

## Cara Menjalankan

1. Buat virtual environment (opsional namun disarankan):
   
   Windows PowerShell:
   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

2. Install dependensi:
   ```powershell
   pip install -r requirements.txt
   ```

3. Jalankan game:
   ```powershell
   python chess_game.py
   ```

## Kontrol
- Klik kiri: pilih bidak putih dan pilih tujuan.
- Tekan ESC atau tutup jendela untuk keluar.

## Catatan
- AI bertindak sebagai hitam dan bergerak otomatis setelah Anda melangkah.
- Evaluasi material sederhana: P=1, N=3, B=3, R=5, Q=9 (raja tidak dinilai).
- Game dianggap selesai jika salah satu raja hilang dari papan atau tidak ada langkah legal tersisa untuk pemain yang giliran.
