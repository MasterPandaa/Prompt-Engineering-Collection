# Chess Game (Python + Pygame)

Game catur standar menggunakan Python dan Pygame.

Fitur:
- Papan 8x8 dengan warna selang-seling.
- Bidak divisualisasikan menggunakan simbol Unicode (tanpa file gambar eksternal).
- Gerak dasar semua bidak (Pawn, Rook, Knight, Bishop, Queen, King).
- Sistem giliran: Putih (Player) vs Hitam (AI sederhana).
- Deteksi skak (Check) dasar.
- AI Hitam memilih langkah acak dari daftar langkah legal.

## Cara Menjalankan
1. Pastikan Python 3.9+ telah terpasang.
2. Instal dependensi:
   ```bash
   pip install -r requirements.txt
   ```
3. Jalankan game:
   ```bash
   python chess_game.py
   ```

## Kontrol
- Klik kiri pada bidak putih untuk memilih.
- Klik petak tujuan untuk melangkah.
- Tekan `R` untuk reset papan.
- Tekan `ESC` untuk keluar.

## Catatan
- Fitur lanjutan seperti castling, en passant, dan tiga kali pengulangan tidak diimplementasikan untuk kesederhanaan.
- Promosi pion otomatis menjadi Queen.
