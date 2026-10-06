# Pacman Pygame Sederhana

Game Pacman sederhana menggunakan Pygame berdasarkan grid layout 2D.

## Fitur
- Render maze dari list 2D (`1 = dinding`, `0 = jalan`, `2 = pelet`, `3 = power-pellet`).
- Pacman bergerak dengan tombol panah (atau WASD) dan memakan pelet/power-pellet.
- 2 hantu AI dengan pergerakan acak di jalur tersedia.
- Status power-up: saat Pacman memakan power-pellet, hantu menjadi takut (biru), bergerak lebih lambat, dan bisa dimakan.
- Skor, nyawa, kondisi menang (semua pelet habis), dan game over.

## Struktur File
- `main.py` — kode utama game.
- `requirements.txt` — dependensi Python.

## Cara Menjalankan
1. Pastikan Python 3.9+ terpasang.
2. (Disarankan) Buat virtual environment.
3. Instal dependensi:
   ```bash
   pip install -r requirements.txt
   ```
4. Jalankan game:
   ```bash
   python main.py
   ```

## Kontrol
- Panah/WASD: Gerak Pacman
- ESC: Keluar
- R: Restart (ketika menang/kalah)

## Catatan Teknis
- Ukuran tile: 64 px. Maze dipusatkan otomatis pada layar 800x600.
- Power-up aktif selama 6 detik. Hantu berkedip putih saat mendekati akhir power-up.
- Deteksi tabrakan menggunakan jarak antar pusat (lingkaran) Pacman dan hantu.

Selamat bermain!
