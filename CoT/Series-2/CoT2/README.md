# Snake (Pygame)

Game Snake klasik menggunakan Pygame.

## Persyaratan

- Python 3.9+
- Pygame (lihat `requirements.txt`)

## Instalasi

Disarankan menggunakan virtual environment.

### Windows (PowerShell)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Menjalankan Game

```powershell
python main.py
```

## Kontrol

- Panah atau WASD untuk mengarahkan ular.
- Saat Game Over: tekan tombol apa pun untuk restart, `ESC` untuk keluar.

## Catatan

- Ukuran grid dapat diubah lewat konstanta `BLOCK` di `main.py`.
- Kecepatan permainan diatur oleh `SNAKE_SPEED` (FPS).
