# Snake Game (Pygame)

Game Snake klasik dibuat dengan Pygame.

## Persyaratan
- Python 3.9+ (disarankan 3.9–3.12)
- Windows (uji coba utama), tetapi juga dapat berjalan di macOS/Linux

## Instalasi
1. Buka PowerShell di folder proyek:
   - Folder: `d:/laragon2/laragon/www/dataset/Snake/chain-of-thought/iterasi6/`

2. (Opsional) Buat virtual environment:
   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. Install dependencies:
   ```powershell
   py -m pip install -r requirements.txt
   ```

## Menjalankan
```powershell
py snake_game.py
```

## Kontrol
- Panah / WASD untuk mengarahkan ular
- Setelah Game Over:
  - R / Enter / Space untuk restart
  - Q / Escape untuk keluar

## Catatan
- Ubah `SNAKE_SPEED` di `snake_game.py` untuk menyesuaikan kecepatan ular.
- Ukuran grid ditentukan oleh `WIDTH`, `HEIGHT`, dan `BLOCK_SIZE`. Semua posisi menggunakan koordinat grid dan digambar dengan mengalikan `BLOCK_SIZE`.
