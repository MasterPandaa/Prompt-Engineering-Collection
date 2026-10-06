# Snake Game (Pygame)

Game Snake sederhana berbasis Pygame.

## Spesifikasi
- Layar 600x400
- Ukuran blok 20x20 piksel
- Kontrol: tombol panah
- Tidak bisa berbalik arah 180° secara langsung
- Makanan acak pada grid 20x20 dan tidak menimpa tubuh ular
- Ular bertambah panjang saat makan
- Game over saat menabrak dinding atau tubuh sendiri
- Skor ditampilkan di layar

## Cara Menjalankan (Windows)
1. Pastikan Python sudah terpasang (cek dengan `python --version`).
2. (Opsional) Buat virtual environment:
   - `python -m venv .venv`
   - PowerShell: `.venv\\Scripts\\Activate.ps1`
3. Instal dependensi:
   - `python -m pip install -r requirements.txt`
4. Jalankan game:
   - `python snake_game.py`

Kontrol saat bermain:
- Panah atas/bawah/kiri/kanan untuk bergerak
- Saat Game Over: tekan `R` untuk restart, `ESC` untuk keluar
