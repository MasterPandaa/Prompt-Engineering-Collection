# Snake (Pygame)

Game Snake klasik dibuat dengan Pygame.

## Persyaratan

- Python 3.9+
- Windows (disarankan; perintah contoh untuk PowerShell)

Instal dependensi:

```powershell
python -m pip install -r requirements.txt
```

## Menjalankan

```powershell
python .\snake.py
```

## Kontrol

- Panah atau WASD untuk menggerakkan ular
- Saat Game Over:
  - R / Enter / Space: Restart
  - Q / Esc: Keluar

## Konfigurasi

Ubah konstanta di bagian atas `snake.py` jika diperlukan:

- `WIDTH`, `HEIGHT`: Resolusi window (harus kelipatan `BLOCK_SIZE`)
- `BLOCK_SIZE`: Ukuran satu sel grid (default 20)
- `SNAKE_SPEED`: FPS game (kecepatan ular)

## Catatan & Troubleshooting

- Jika window tidak muncul di depan, coba alt-tab atau jalankan dari terminal (PowerShell).
- Jika terjadi error `ModuleNotFoundError: No module named 'pygame'`, pastikan instalasi: `python -m pip install -r requirements.txt`.
- Beberapa antivirus/SmartScreen dapat menanyakan perizinan untuk program yang membuka window grafis; izinkan jika aman.
