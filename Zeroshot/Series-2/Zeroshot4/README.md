# Snake (Pygame)

Game Snake klasik dibuat dengan Python dan Pygame.

## Spesifikasi
- Resolusi layar: 600x400 piksel.
- Kontrol: Panah (atau WASD) untuk arah.
- Aturan: Tidak bisa membalik arah langsung (mis. kanan -> kiri).
- Ular tumbuh + skor bertambah saat memakan makanan.
- Game Over jika menabrak dinding atau tubuh sendiri.

## Persyaratan
- Python 3.8+ (disarankan 3.10/3.11)
- Pygame (lihat `requirements.txt`)

## Cara Menjalankan (Windows)
1. (Opsional) Buat virtual environment:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
2. Instal dependensi:
   ```powershell
   python -m pip install -r requirements.txt
   ```
3. Jalankan game:
   ```powershell
   python main.py
   ```

## Kontrol
- Panah Atas/Bawah/Kiri/Kanan atau W/A/S/D untuk mengarahkan ular.
- Saat Game Over:
  - R: Restart
  - ESC atau Q: Keluar

## Catatan
- Kecepatan game diatur pada 12 FPS (klasik). Anda bisa menyesuaikan nilai `clock.tick(12)` di `main.py`.
- Grid digambar tipis untuk estetika; bisa diaktifkan dengan membuka komentar fungsi `draw_grid(screen)`.
