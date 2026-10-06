# Snake Game (Pygame)

Klasik game Snake dibuat dengan Python dan Pygame.

## Spesifikasi
- Layar: 600 x 400 piksel
- Kontrol: Tombol panah (↑ ↓ ← →), tidak bisa memutar balik arah secara langsung
- Makanan: Muncul acak, menambah panjang ular dan skor +1
- Game Over: Menabrak dinding atau tubuh sendiri
- Tampilkan skor
- Restart: Tekan R/Enter/Space, Keluar: Q/Esc atau tutup jendela

## Persiapan
1. Pastikan Python 3.8+ terpasang.
2. Instal dependensi:
   ```bash
   pip install -r requirements.txt
   ```

## Menjalankan
```bash
python snake_game.py
```

## Catatan
- Kecepatan ular dapat diatur melalui variabel `FPS` di `snake_game.py`.
- Ukuran grid (besar segmen ular dan makanan) ada di `BLOCK_SIZE`.
