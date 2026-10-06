# Tetris (Pygame)

Implementasi lengkap game Tetris menggunakan Pygame.

## Fitur
- Grid 10x20 sesuai standar Tetris.
- 7 bentuk tetromino (I, O, T, S, Z, J, L) dengan rotasi.
- Deteksi tabrakan (dinding, dasar, dan bidak terkunci).
- Pembersihan baris penuh dan perhitungan skor (Tetris scoring sederhana).
- Sistem bag/queue 7 (random adil) dan preview next pieces.
- Hard drop, soft drop, dan wall-kick sederhana.

## Kontrol
- Panah Kiri/Kanan: Geser bidak.
- Panah Bawah: Soft drop.
- Panah Atas / X: Rotasi searah jarum jam.
- Z: Rotasi berlawanan arah jarum jam.
- Spasi: Hard drop.
- C: Toggle fast drop (gravitasi cepat sementara).
- ESC: Keluar.
- R (saat Game Over): Restart.

## Cara Menjalankan
1. Pastikan Python 3.8+ sudah terpasang.
2. Instal dependensi:
   ```bash
   pip install -r requirements.txt
   ```
3. Jalankan game:
   ```bash
   python main.py
   ```

## Catatan
- Game berjalan di 60 FPS. Kecepatan jatuh meningkat seiring level (berdasarkan skor).
- Skor per clear: 1/2/3/4 baris = 100/300/500/800, dikali level.
