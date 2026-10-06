# Pacman (Pygame)

Implementasi sederhana game Pacman menggunakan Pygame.

## Fitur
- Render maze berbasis grid dari list 2D.
- Pacman bergerak dengan tombol panah dan memakan pellet (2) dan power-pellet (3).
- 2 hantu AI dengan logika gerak acak pada jalur yang tersedia.
- Logika tabrakan Pacman-Hantu dan status power-up (makan hantu saat power aktif).
- HUD skor, nyawa, dan indikator power.

## Dependensi
- Python 3.9+
- Pygame (lihat `requirements.txt`)

## Cara Menjalankan
1. Buat virtual environment (opsional namun direkomendasikan).
2. Install dependensi:
   ```bash
   pip install -r requirements.txt
   ```
3. Jalankan game:
   ```bash
   python pacman.py
   ```

## Kontrol
- Panah Kiri/Kanan/Atas/Bawah: Gerak Pacman
- R: Restart saat menang/kalah
- Esc: Keluar

## Catatan
- Ukuran tile `48px`, resolusi akan menyesuaikan ukuran maze + area HUD.
- Anda dapat mengubah layout maze pada konstanta `MAZE_LAYOUT` di `pacman.py`.
