# Pacman (Pygame)

Game Pacman sederhana berbasis Pygame dengan fitur:

- Maze grid-based statis (`#` dinding, `.` pelet, `o` power-pellet, `P` posisi awal Pacman, `G` posisi awal hantu)
- Gerakan Pacman tile-based dengan input arah (WASD/Arrow)
- Deteksi tabrakan dinding, makan pelet & power-pellet
- Hantu dengan AI sederhana (pilih arah acak di persimpangan, hindari langsung berbalik), mode frightened saat power aktif
- HUD skor dan nyawa, state `gameover`

## Cara Menjalankan

1) Buat dan aktifkan environment (opsional tapi direkomendasikan)

Windows (PowerShell):
```
python -m venv .venv
.venv\Scripts\Activate.ps1
```

2) Instal dependensi
```
pip install -r requirements.txt
```

3) Jalankan game
```
python pacman.py
```

## Kontrol

- Arah: Panah (↑ ↓ ← →) atau WASD
- Keluar: Esc
- Restart saat Game Over: Enter / Space

## Catatan Teknis

- File utama: `pacman.py`
- Dependensi: `pygame`
- Ukuran tile default: 24 px; resolusi menyesuaikan ukuran maze
- Tunnel wrapping horizontal diaktifkan
- Power-up berlangsung ~6 detik; selama frightened, hantu lebih lambat dan dapat dimakan

Selamat bermain!
