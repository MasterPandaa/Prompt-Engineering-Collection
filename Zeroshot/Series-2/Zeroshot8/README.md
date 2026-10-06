# Snake (Pygame)

Game Snake klasik menggunakan Python dan Pygame.

## Spesifikasi
- Resolusi layar: 600x400 piksel
- Kontrol: Panah Atas/Bawah/Kiri/Kanan
- Aturan: Tidak bisa langsung berbalik arah (misal: kanan -> kiri)
- Makanan muncul acak, skor +1, ular bertambah 1 segmen
- Game Over jika menabrak dinding atau tubuh sendiri
- Tampilkan skor di layar

## Menjalankan
1. Pastikan Python 3.8+ sudah terpasang.
2. (Opsional) Buat virtual environment.
3. Install dependency:
   ```bash
   pip install -r requirements.txt
   ```
4. Jalankan game:
   ```bash
   python snake_game.py
   ```

## Kontrol
- Panah Kanan/Kiri/Atas/Bawah: Ubah arah gerak
- R (saat Game Over): Mulai ulang
- Esc: Keluar

## Catatan
- Kecepatan ular dapat diubah pada konstanta `FPS` di `snake_game.py`.
- Ukuran grid dapat diubah pada `TILE_SIZE`, pastikan `WIDTH` dan `HEIGHT` adalah kelipatan dari `TILE_SIZE`.
