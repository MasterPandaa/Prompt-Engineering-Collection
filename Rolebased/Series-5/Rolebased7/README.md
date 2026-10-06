# Mini Chess Engine (Python + Pygame)

Engine catur mini yang playable, modular, dan sederhana:

- Board dan Rules dipisah (`Board`, `Rules`).
- Rendering bidak menggunakan Unicode Chess via `pygame.font.SysFont`.
- AI sederhana (greedy capture) berbasis evaluasi material.
- Interaksi klik: pilih petak, lalu klik tujuan. Petak terpilih dan tujuan disorot.
- Promosi otomatis ke Queen.

## Struktur File

- `chess_mini.py` — kode utama game + engine.
- `requirements.txt` — dependensi Python (pygame).

## Menjalankan

1) Buat dan aktifkan virtual env (opsional, tapi disarankan)

Windows PowerShell:
```powershell
python -m venv .venv
.venv\\Scripts\\Activate.ps1
```

2) Instal dependensi
```powershell
pip install -r requirements.txt
```

3) Jalankan game
```powershell
python chess_mini.py
```

## Catatan

- Default: pemain Putih (Anda) vs AI Hitam.
- Tidak termasuk: cek/cekmat penuh, en passant, castling.
- Promosi otomatis menjadi Queen.
- Jika glyph Unicode tidak tampil sempurna, ganti font fallback di fungsi `get_font()`.
