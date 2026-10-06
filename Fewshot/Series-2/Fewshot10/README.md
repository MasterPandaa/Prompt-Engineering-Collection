# Snake Game (Pygame)

Game Snake sederhana menggunakan Pygame.

## Spesifikasi
- Layar: 600x400
- Ukuran blok: 20x20
- Kontrol: Arrow Keys / WASD
- Fitur: makanan acak, ular bertambah panjang saat makan, deteksi tabrakan dinding & tubuh sendiri, skor, layar Game Over dengan restart.

## Persyaratan
- Python 3.8+
- Pygame (lihat `requirements.txt`)

## Cara Menjalankan (Windows / PowerShell)
1. Buat virtual environment (opsional tapi disarankan):
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
2. Instal dependensi:
   ```powershell
   pip install -r requirements.txt
   ```
3. Jalankan game:
   ```powershell
   python snake.py
   ```

## Kontrol
- Panah/WASD untuk bergerak
- ESC untuk keluar saat bermain
- Di layar Game Over: R untuk restart, Q/ESC untuk keluar

## Catatan
- Ubah nilai `FPS` di `snake.py` untuk menyesuaikan kecepatan permainan.
- Aktifkan fungsi `draw_grid(screen)` (di-comment) jika ingin melihat grid bantuan.
