# Pong dengan AI (Pygame)

Game Pong sederhana menggunakan Pygame.

## Spesifikasi
- Layar 800x600.
- Paddle kiri (pemain) dikontrol dengan tombol `W` (atas) dan `S` (bawah).
- Paddle kanan (AI) mengikuti posisi Y bola dengan kecepatan maksimum agar tetap fair.
- Bola memantul pada dinding atas/bawah dan pada paddle (pantulan dipengaruhi titik tumbukan dan sedikit kecepatan paddle).
- Sistem skor ditampilkan di atas. Batas nilai default: 10. Tekan `R` untuk restart saat ada pemenang.

## Cara Menjalankan (Windows)
1. Pastikan Python 3.9+ terpasang.
2. (Opsional) Buat virtual environment.
3. Install dependensi:
   ```bash
   pip install -r requirements.txt
   ```
4. Jalankan game:
   ```bash
   python pong_ai.py
   ```

## Kontrol
- `W`: Gerak paddle pemain ke atas
- `S`: Gerak paddle pemain ke bawah
- `R`: Reset skor saat pertandingan selesai
- `Alt+F4` atau tutup jendela untuk keluar

## Catatan
- Jika FPS terlalu tinggi/rendah, Anda bisa menyesuaikan `PLAYER_SPEED`, `AI_MAX_SPEED`, dan `BALL_SPEED_INITIAL` di `pong_ai.py`.
