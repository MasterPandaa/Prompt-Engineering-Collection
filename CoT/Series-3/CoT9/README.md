# Pacman (Pygame)

Game Pacman sederhana berbasis Pygame. Mendukung:
- Maze grid-based (dinding `#`, pelet `.`, power-pellet `o`, spawn `P`/`G`).
- Gerakan Pacman berbasis tile dan input arah buffered.
- Ghost AI sederhana: memilih arah valid di persimpangan, menghindari berbalik, mode frightened, dan eaten.
- Power-up yang membuat ghost frightened dan bisa dimakan.
- State permainan: skor, nyawa, level naik saat semua pelet habis.

## Persyaratan
- Python 3.9+
- Windows (direkomendasikan; Linux/Mac juga umumnya berjalan)

## Instalasi

1. Buat virtual environment (opsional tapi disarankan):
   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
2. Instal dependensi:
   ```powershell
   pip install -r requirements.txt
   ```

Jika mengalami masalah SDL di Windows, pastikan VS redistributable/driver GPU terbaru telah terpasang.

## Menjalankan

```powershell
py pacman.py
```

Kontrol:
- Panah arah untuk bergerak.
- ESC untuk keluar.
- Saat Game Over, tekan SPACE atau ENTER untuk restart.

## Struktur Kode
- `pacman.py`: berisi class utama `Maze`, `Pacman`, `Ghost`, dan `Game`.
  - `Maze`: parsing layout, daftar dinding/pelet/power, utilitas validasi tile dan gambar maze.
  - `Pacman`: input buffered (`next_dir`), ganti arah di pusat tile, makan pelet dan power.
  - `Ghost`: state `normal`/`frightened`/`eaten`, pemilihan arah di persimpangan secara sederhana.
  - `Game`: manajemen skor, nyawa, timer power, update loop dan rendering.

## Kustomisasi
- Ubah `MAZE_LAYOUT` di `pacman.py` untuk desain maze.
- Ubah konstanta kecepatan atau durasi power-up di bagian konfigurasi.

Selamat bermain!
