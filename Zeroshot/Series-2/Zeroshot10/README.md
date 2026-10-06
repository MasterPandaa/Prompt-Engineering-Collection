# Snake Game (Pygame)

Game Snake klasik dibuat dengan Python dan Pygame.

## Spesifikasi
- Layar permainan: 600x400 piksel.
- Ular mulai dari tengah, bergerak terus-menerus di grid 20px.
- Kontrol arah: tombol panah (atas/bawah/kiri/kanan). Tidak bisa membalik arah langsung.
- Makanan muncul acak, makan menambah panjang 1 segmen dan skor +1.
- Game Over saat menabrak dinding atau tubuh sendiri.
- Menampilkan skor di layar.

## Persyaratan
- Python 3.8+
- Pygame

## Instalasi
1. (Opsional) Buat dan aktifkan virtual environment
   - Windows PowerShell:
     ```powershell
     python -m venv venv
     .\venv\Scripts\Activate.ps1
     ```

2. Install dependensi
   ```powershell
   pip install -r requirements.txt
   ```

## Menjalankan
```powershell
python snake_game.py
```

## Kontrol
- Panah Atas/Bawah/Kiri/Kanan: ubah arah ular.
- Saat Game Over:
  - ENTER: main lagi
  - ESC: keluar

## Catatan
- Grid berukuran 20px; posisi ular dan makanan selaras dengan grid.
- Garis grid dimatikan secara default. Anda bisa mengaktifkan fungsi `draw_grid(screen)` di `snake_game.py` untuk melihat grid.
