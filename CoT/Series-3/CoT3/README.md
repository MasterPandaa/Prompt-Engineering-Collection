# Pacman (Pygame)

Game Pacman sederhana berbasis Pygame dengan maze grid, pelet, power-pellet, empat hantu dengan AI sederhana, dan manajemen state dasar.

## Fitur
- Maze grid statis berbasis string.
- Pacman bergerak grid-aware dengan input keyboard (WASD / panah), makan pelet dan power-pellet.
- Hantu (Blinky, Pinky, Inky, Clyde) dengan AI sederhana:
  - Menghindari berbalik arah jika memungkinkan.
  - Memilih arah acak di persimpangan.
  - Mode frightened saat Pacman makan power-pellet (bergerak lebih lambat dan bisa dimakan).
  - Saat dimakan, hantu kembali ke rumah lalu kembali ke mode chase.
- State permainan: playing, win, gameover.
- HUD skor dan nyawa.

## Persyaratan
- Python 3.9+
- Pygame (lihat `requirements.txt`)

## Instalasi
```bash
pip install -r requirements.txt
```

## Menjalankan
```bash
python main.py
```

- Tekan `Esc` untuk keluar.
- Saat `WIN` atau `GAME OVER`, tekan `R` untuk restart.

## Struktur Kode
- `main.py`
  - `MAZE_LAYOUT`: representasi maze dengan simbol `#` (dinding), `.` (pelet), `o` (power-pellet), `G` (gerbang rumah hantu), spasi (jalan kosong).
  - `Player`: input, gerakan, makan pelet/power, skor dan nyawa.
  - `Ghost`: AI sederhana (pilih arah pada persimpangan, frightened, eaten/respawn).
  - `Game`: loop utama, update, render, HUD, state.

## Catatan
- Ukuran tile 24px; resolusi menyesuaikan ukuran layout.
- Mekanika sederhana untuk memudahkan implementasi: gerbang `G` hanya dilewati hantu yang sedang `eaten` untuk respawn.
- Terdapat wrap horizontal (tunnel) di sisi kiri/kanan layar.
