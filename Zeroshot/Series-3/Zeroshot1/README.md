# Pacman (Pygame)

Game Pacman klasik dengan Python dan Pygame.

## Fitur
- Layar 800x600 (grid 40x30, tile 20px)
- Maze 2D di-hardcode (`'1'=dinding`, `'0'=jalan`, `'2'=pelet`, `'3'=power-pellet`)
- Pacman dikontrol tombol arah, tidak bisa menembus dinding
- 4 Hantu dengan AI sederhana (mengejar/menjauh saat vulnerable)
- Power-pellet membuat hantu rentan sementara
- Skor, nyawa, menang (habis pelet) / kalah (nyawa habis)
- Restart dengan tombol `R`

## Instalasi

1. Pastikan Python 3.9+ terpasang.
2. Install dependensi:

```bash
pip install -r requirements.txt
```

Jika menggunakan venv di Windows (opsional):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Menjalankan Game

```bash
python main.py
```

Kontrol:
- Panah kiri/kanan/atas/bawah untuk bergerak
- ESC untuk keluar
- R untuk restart saat layar Game Over/Menang

## Catatan Teknis
- Tunnel wrap kiri/kanan di baris tengah
- Ghost house di tengah; saat dimakan, hantu menjadi "mata" yang pulang ke markas lalu respawn
- Kecepatan dan durasi vulnerable bisa diatur di konstanta atas file `main.py`
