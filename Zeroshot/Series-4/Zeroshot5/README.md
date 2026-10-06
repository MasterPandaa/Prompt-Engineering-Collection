# Tetris (Python + Pygame)

Game Tetris klasik dibuat dengan Python dan Pygame.

## Spesifikasi Utama
- Papan 10 kolom x 20 baris, ukuran blok 30 piksel.
- 7 Tetromino: I, O, T, S, Z, J, L dengan warna berbeda.
- Kontrol:
  - Panah Kiri/Kanan: Gerak horizontal
  - Panah Bawah: Soft drop (mempercepat jatuh)
  - Panah Atas: Rotasi
  - SPACE: Hard drop (langsung ke posisi terendah)
- Mekanik: spawn di tengah atas, penguncian saat menyentuh dasar/bidak lain, clear line, skor, game over saat papan penuh.

## Persiapan
1. Pastikan Python 3.8+ terpasang.
2. Install dependensi:
   ```bash
   pip install -r requirements.txt
   ```

## Menjalankan
```bash
python tetris.py
```

## Catatan
- Tekan `ESC` untuk keluar saat bermain.
- Skor bertambah saat Anda menghapus baris (1-4 baris sekaligus memiliki skor berjenjang).
