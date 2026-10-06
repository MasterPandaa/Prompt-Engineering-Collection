# Pacman (Pygame)

Game Pacman klasik sederhana dibuat dengan Python dan Pygame.

## Spesifikasi
- Resolusi layar: 800x600
- Maze di-hardcode menggunakan grid 2D
- Kontrol: panah (atas/bawah/kiri/kanan), ESC untuk keluar, R untuk restart saat menang/kalah
- Fitur: pelet, power-pellet, 4 hantu (AI sederhana), skor, nyawa, kondisi menang/kalah

## Cara Menjalankan
1. Pastikan Python 3.9+ terpasang.
2. Install dependensi:
   ```bash
   pip install -r requirements.txt
   ```
3. Jalankan game:
   ```bash
   python pacman.py
   ```

## Catatan
- Power-pellet membuat hantu rentan untuk beberapa detik. Saat rentan, jika disentuh Pacman, hantu menjadi "eyes" dan kembali ke markas, lalu respawn normal.
- Sistem skor: pelet (+10), power-pellet (+50), hantu saat rentan (+200).
- Nyawa awal: 3. Game over jika nyawa habis; menang jika semua pelet dimakan.
