# Pacman Clone (Python + Pygame)

Klona Pacman sederhana berbasis OOP menggunakan Python dan Pygame.

## Fitur
- Kelas terpisah: `Game`, `Maze`, `Player`, `Ghost`.
- Maze dirender dari layout 2D yang di-hardcode (lihat `Maze` di `main.py`).
- Dua AI hantu yang berbeda:
  - `chaser`: Mengejar pemain menggunakan BFS (langkah terdekat).
  - `random`: Bergerak acak dan mengubah arah secara berkala.
- Power-pellet membuat hantu menjadi `vulnerable`. Saat dalam kondisi ini, Pacman dapat memakan hantu.
- Tunneling/wrap sederhana di tepi peta.

## Persyaratan
- Python 3.9+ direkomendasikan.
- Pygame (lihat `requirements.txt`).

## Cara Menjalankan
1. Buat virtualenv (opsional namun direkomendasikan):
   - Windows PowerShell:
     ```powershell
     py -m venv .venv
     .venv\Scripts\Activate.ps1
     ```
2. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
3. Jalankan game:
   ```powershell
   python main.py
   ```

## Kontrol
- Arah: `WASD` atau `Arrow Keys`.
- Keluar: `Esc`.
- Restart saat menang/kalah: `Enter`.

## Struktur
- `main.py`: Seluruh implementasi game.
- `requirements.txt`: Daftar dependensi.

## Catatan
- Ukuran tile `24px`. Layar termasuk panel UI di bagian atas.
- Kecepatan, durasi power, dan warna dapat diubah melalui konstanta di bagian atas `main.py`.
