# Pacman (Pygame)

Game Pacman sederhana berbasis Pygame dengan:

- Render maze dari struktur data 2D (1: dinding, 0: kosong, 2: pelet, 3: power-pellet)
- Pacman dapat bergerak dengan tombol panah dan memakan pelet
- 2 hantu AI yang bergerak acak di jalur yang tersedia
- Logika tabrakan dan mode power-up (hantu jadi frightened)

## Persyaratan

- Python 3.8+
- Pygame (otomatis terpasang dari `requirements.txt`)

## Cara Menjalankan

Disarankan menggunakan virtual environment.

1) Buat virtual environment (opsional namun direkomendasikan):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2) Install dependencies:

```powershell
pip install -r requirements.txt
```

3) Jalankan game:

```powershell
python main.py
```

## Kontrol

- Panah Kiri/Kanan/Atas/Bawah: Gerakkan Pacman
- ESC: Keluar
- R: Restart saat layar game over/win

## Aturan Game Singkat

- Pelet kecil (2) bernilai 10 poin
- Power-pellet (3) bernilai 50 poin dan mengaktifkan mode power selama beberapa detik
- Saat mode power aktif, Pacman dapat “memakan” hantu untuk 200 poin
- Jika tersentuh hantu saat tidak dalam mode power, Pacman kehilangan 1 nyawa
- Menang jika semua pelet habis

## Struktur Proyek

- `main.py`: Kode utama game
- `requirements.txt`: Daftar dependency
- `README.md`: Petunjuk penggunaan

## Catatan Teknis

- Ukuran tile: 64 px
- Ukuran jendela otomatis dihitung dari ukuran grid dan tinggi UI bar (64 px)
- Hantu bergerak acak di persimpangan dan cenderung tidak berbalik arah kecuali diperlukan
