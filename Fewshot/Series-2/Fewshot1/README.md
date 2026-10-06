# Game Snake (Pygame)

Game Snake sederhana menggunakan Pygame.

## Spesifikasi
- Layar: 600 x 400
- Ukuran blok: 20 x 20
- Kontrol: tombol panah (tidak bisa berbalik arah langsung)
- Fitur: makanan acak, panjang ular bertambah saat makan, deteksi tabrakan dinding dan tubuh sendiri, skor ditampilkan

## Persyaratan
- Python 3.8+
- Pygame (tercantum di `requirements.txt`)

## Cara Menjalankan
1. Buat dan aktifkan virtual environment (opsional, direkomendasikan)
2. Instal dependensi
3. Jalankan game

### Windows (PowerShell)
```powershell
# 1) (Opsional) Buat venv
python -m venv .venv
. .\.venv\Scripts\Activate.ps1

# 2) Install dependensi
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# 3) Jalankan game
python snake.py
```

Jika `python` mengarah ke Python versi lain, Anda bisa memakai `py`:
```powershell
py -m pip install -r requirements.txt
py snake.py
```

## Kontrol
- Panah Atas/Bawah/Kiri/Kanan: Gerakkan ular
- Esc: Keluar
- Setelah Game Over: R untuk main lagi, Q/Esc untuk keluar

## Struktur Proyek
- `snake.py` — kode utama game
- `requirements.txt` — daftar dependensi
- `README.md` — petunjuk penggunaan
