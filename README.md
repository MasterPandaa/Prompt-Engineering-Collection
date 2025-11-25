# Pacman (Pygame)

Game Pacman sederhana berbasis Pygame dengan fitur inti:

- Maze grid-based statis (dinding, pelet, power-pellet)
- Pacman: gerak halus per-tile, input keyboard, makan pelet dan power-up
- Ghost: AI sederhana (hindari balik arah, pilih arah di persimpangan, takut saat power-up)
- State: normal, power-up (timer), game over, win
- HUD: skor, nyawa, dan sisa waktu power-up

## Cara Menjalankan

1. Buat environment Python 3.9+ (disarankan).
2. Install dependency:

```bash
pip install -r requirements.txt
```

3. Jalankan game:

```bash
python main.py
```

## Kontrol

- Panah / WASD untuk bergerak
- ESC untuk keluar
- R untuk restart saat Game Over atau Win

## Struktur Kode

- `main.py`: seluruh implementasi game.
  - `Maze`: mem-parsing `MAZE_LAYOUT`, menggambar dinding dan pelet.
  - `Pacman`: mengelola input, gerak halus, dan animasi mulut.
  - `Ghost`: AI sederhana dengan state `NORMAL`, `FRIGHTENED`, `EATEN`.
  - `Game`: loop utama, state machine (NORMAL, POWER, WIN, GAME_OVER), skor, nyawa, rendering.

## Catatan

- Level layout didefinisikan di konstanta `MAZE_LAYOUT` pada `main.py`. Anda bisa memodifikasi karakter:
  - `#` dinding
  - `.` pelet
  - `o` power-pellet
  - `P` posisi awal Pacman
  - `G` posisi awal Ghost

Selamat bermain!
