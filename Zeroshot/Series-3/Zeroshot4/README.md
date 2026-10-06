# Pacman (Python + Pygame)

Game Pacman klasik dengan Python dan Pygame.

## Spesifikasi
- Layar: 800x600 piksel (grid 40x30 dengan tile 20px).
- Maze: layout 2D di-hardcode. `'1'` = dinding, `'0'`/`'2'` = jalur + pelet, `'3'` = power-pellet.
- Pacman: Dikontrol tombol panah. Tidak bisa menembus dinding.
- Pelet: Makan semua pelet untuk menang.
- Power-Pellets: Membuat hantu rentan (biru) sementara.
- Hantu: 4 hantu dengan AI sederhana (mengejar atau menghindari saat rentan), kembali ke markas ketika tertangkap saat rentan.
- HUD: Skor dan nyawa.

## Menjalankan
1) Instal dependensi (Pygame):

   ```bash
   pip install -r requirements.txt
   ```

2) Jalankan game:

   ```bash
   python pacman_game.py
   ```

## Kontrol
- Panah kiri/kanan/atas/bawah untuk bergerak
- Esc untuk keluar
- Enter di layar Game Over/You Win untuk restart

## Catatan
- Saat restart (Enter), maze dan pelet direset otomatis.
- Grid menggunakan tile 20px sehingga posisi dan gerak selaras grid.
