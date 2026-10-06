# Snake (Pygame)

## Cara Menjalankan

1. (Opsional) Buat dan aktifkan virtual env.
   - PowerShell:
     ```powershell
     python -m venv venv
     .\venv\Scripts\Activate.ps1
     ```
2. Install dependensi:
   ```powershell
   pip install -r requirements.txt
   ```
3. Jalankan game:
   ```powershell
   python snake.py
   ```

## Kontrol
- Panah/WASD untuk bergerak
- R untuk restart saat Game Over
- Esc atau Q untuk keluar saat Game Over

## Catatan
- Kecepatan ular diatur oleh variabel `FPS` di `snake.py`.
- Ukuran grid ditentukan `BLOCK_SIZE`.
- Skor ditampilkan di kiri atas layar.
