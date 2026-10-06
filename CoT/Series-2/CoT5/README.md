# Snake Game (Pygame)

Game Snake klasik dibuat dengan Pygame.

## Prasyarat
- Python 3.8+ (disarankan 3.10+)
- Pip

## Instalasi
```powershell
# Dari folder proyek
pip install -r requirements.txt
```

## Menjalankan
```powershell
python snake.py
```

## Kontrol
- Panah atau WASD: Gerak
- R / Enter / Space: Restart saat Game Over
- Q / Esc: Keluar

## Pengaturan
Anda dapat menyesuaikan variabel di `snake.py`:
- `WIDTH`, `HEIGHT`: Resolusi
- `BLOCK_SIZE`: Ukuran grid
- `SPEED`: Kecepatan/Frame per detik

## Catatan
- Makanan tidak akan muncul di atas tubuh ular.
- Ular tidak bisa berbalik 180° secara langsung.
