# Pacman Pygame (Contoh Sederhana)

Game Pacman sederhana menggunakan Pygame, berdasarkan grid 2D.

Fitur:
- Render maze dari list 2D (`1` dinding, `2` pelet kecil, `3` power pellet, `0` jalan kosong)
- Pacman bergerak dengan tombol panah dan memakan pelet
- 2 hantu dengan AI sederhana (bergerak acak di jalur yang tersedia)
- Power-up (Power Pellet) membuat hantu ketakutan untuk beberapa detik
- Skor, HUD, kondisi menang/kalah, dan restart (tombol `R`)

## Persyaratan
- Python 3.9+
- Pygame (lihat `requirements.txt`)

## Instalasi
Di terminal/PowerShell:

```bash
pip install -r requirements.txt
```

## Menjalankan
Di direktori proyek yang sama:

```bash
python main.py
```

## Kontrol
- Panah Kiri/Kanan/Atas/Bawah: Gerakkan Pacman
- R: Restart (ketika Game Over atau Menang)
- Esc: Keluar

## Struktur
- `main.py`: Kode utama game
- `requirements.txt`: Dependensi
- `README.md`: Instruksi

## Catatan
- Ukuran tile (`TILE_SIZE`) dapat diubah di `main.py`.
- Kecepatan Pacman dan hantu, serta durasi power-up dapat diatur melalui konstanta di `main.py`.
