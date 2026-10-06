# Snake Game (Pygame)

Game Snake sederhana yang dibuat dengan Pygame.

## Spesifikasi
- Layar: 600 x 400 px
- Ukuran blok: 20 x 20 px
- Kontrol: Panah (Atas/Bawah/Kiri/Kanan)
- Fitur: Makanan acak, ular bertambah panjang saat makan, deteksi tabrakan dinding dan tubuh sendiri, skor, Game Over overlay + restart

## Menjalankan
1. Buat dan aktifkan virtualenv (opsional, tetapi direkomendasikan)
2. Instal dependensi:
   ```bash
   pip install -r requirements.txt
   ```
3. Jalankan game:
   ```bash
   python snake_game.py
   ```

## Kontrol
- Panah Atas/Bawah/Kiri/Kanan untuk bergerak
- Saat Game Over:
  - Tekan `R` untuk restart
  - Tekan `Esc` atau `Q` untuk keluar

## Catatan
- Kecepatan ular dapat diatur di variabel `SNAKE_SPEED` di `snake_game.py`.
