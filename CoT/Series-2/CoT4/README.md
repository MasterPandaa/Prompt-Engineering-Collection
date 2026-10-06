# Snake Game (Pygame)

## Cara Menjalankan (Windows PowerShell)

1. (Opsional) Buat virtual environment
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
2. Instal dependensi
   ```powershell
   python -m pip install -U pip
   pip install -r requirements.txt
   ```
3. Jalankan game
   ```powershell
   python snake_game.py
   ```

## Kontrol
- Panah atau WASD untuk mengarahkan ular.
- R untuk restart ketika Game Over.
- ESC atau tombol close window untuk keluar.

## Catatan
- Game berjalan pada grid `20x20` piksel per sel.
- Kecepatan ular diatur melalui FPS (`SNAKE_SPEED`).
- Makanan tidak akan muncul di posisi yang ditempati tubuh ular.
