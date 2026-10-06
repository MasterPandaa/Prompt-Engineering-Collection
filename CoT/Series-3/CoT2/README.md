# Pacman (Pygame)

Game Pacman sederhana menggunakan Pygame. Menyertakan maze grid-based, player (Pacman), 4 hantu dengan AI sederhana, pelet & power-pellet, state power-up, skor, dan nyawa.

## Fitur
- Maze statis berbasis grid (dinding `#`, pelet `.`, power `o`, start `P`/`G`).
- Gerakan Pacman dengan input keyboard (panah / WASD) dan collision dengan dinding.
- Deteksi makan pelet & power-pellet, perhitungan skor.
- Hantu dengan AI sederhana: menghindari putar balik, memilih arah acak dengan bias ke/menjauhi Pacman; saat frightened bergerak menjauh; saat dimakan kembali ke rumah.
- State permainan: `playing`, `power`, `gameover`. Timer power-up 8 detik.
- HUD menampilkan skor, nyawa, mode, dan timer power.

## Persyaratan
- Python 3.9+
- Pygame

Install dependencies:

```bash
pip install -r requirements.txt
```

## Menjalankan

```bash
python pacman.py
```

Kontrol:
- Panah atau WASD untuk bergerak.
- ESC untuk keluar.
- Saat `GAME OVER`, tekan `R` untuk restart.

## Struktur File
- `pacman.py` — kode utama game.
- `requirements.txt` — dependensi.
- `README.md` — dokumen ini.

## Catatan Teknis
- Ukuran tile: 24px. Ukuran layar menyesuaikan jumlah kolom/baris pada layout.
- Collision berbasis sel; entitas hanya boleh bergerak ke sel non-dinding.
- Wrap horizontal pada tunnel (keluar kiri muncul di kanan, dan sebaliknya).
- Level selesai saat semua pelet dan power-pellet habis; level di-reset dan skor/nyawa dipertahankan.
