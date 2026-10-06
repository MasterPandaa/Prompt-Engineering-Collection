# Snake (Pygame)

Game Snake sederhana, bersih, dan efisien menggunakan Pygame.

## Fitur
- Ukuran layar 600x400 dengan grid 20px.
- Class `Snake` dan `Food` untuk menjaga loop utama tetap bersih.
- Kontrol panah yang responsif dengan guard untuk mencegah berbalik arah.
- Pertumbuhan ular akurat setelah memakan makanan.
- Penempatan makanan acak yang efisien tanpa menabrak tubuh ular.
- Deteksi tabrakan dinding dan tubuh sendiri.

## Persyaratan
- Python 3.9+
- Lihat `requirements.txt`.

## Cara Menjalankan
1. (Opsional) Buat virtual environment
   - Windows PowerShell:
     ```powershell
     python -m venv .venv
     .venv\\Scripts\\Activate.ps1
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
- Panah atas/bawah/kiri/kanan untuk bergerak.
- Saat Game Over:
  - `R` untuk restart.
  - `Esc` untuk keluar.

## Catatan Teknis
- Grid dihitung dari `CELL_SIZE` agar pergerakan presisi sel.
- Update pergerakan diatur dengan timer event Pygame untuk konsistensi framerate.
- `Snake.set_direction()` memiliki guard clause untuk mencegah 180° turn.
- `Food.spawn()` memilih posisi dari himpunan sel bebas untuk efisiensi.
