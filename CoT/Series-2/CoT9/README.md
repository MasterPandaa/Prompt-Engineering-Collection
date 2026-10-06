# Snake (Pygame)

Game Snake klasik dibuat dengan Pygame.

## Persyaratan
- Python 3.8+
- Pygame (lihat `requirements.txt`)

## Instalasi (Windows PowerShell)
```powershell
# Dari direktori proyek
python -m venv venv
./venv/Scripts/Activate.ps1
pip install -r requirements.txt
```

## Menjalankan
```powershell
python snake.py
```

## Kontrol
- Panah atau WASD: Gerak
- Esc: Keluar
- Enter (di layar Game Over/Win): Main lagi

## Catatan Teknis
- Ukuran grid ditentukan oleh `BLOCK_SIZE` (default 20px).
- Kecepatan game diatur oleh `FPS` (default 12).
- Ular direpresentasikan sebagai list koordinat grid, kepala pada indeks 0.
