# Pacman (Python + Pygame)

Implementasi sederhana game Pacman klasik menggunakan Python dan Pygame.

## Spesifikasi
- Layar: 800x600 piksel (grid 32x24, tile 25px)
- Maze: Hardcode 2D ('1' = dinding, '0' = jalur, '2' = pelet, '3' = power-pellet, '4' = gate rumah hantu, '5' = area rumah hantu)
- Pacman: Gerak grid-based (tombol panah), tidak menembus dinding
- Pelet: Tambah skor
- Power-Pellet: Hantu menjadi frightened (rentan) sementara
- Hantu: 4 hantu dengan AI sederhana (mengejar dengan jarak Manhattan; frightened bergerak acak)
- Mekanisme: Menyentuh hantu normal -> kehilangan nyawa. Menyentuh hantu frightened -> hantu balik ke rumah
- HUD: Skor dan nyawa
- Menang: Semua pelet habis. Game over: nyawa habis

## Kebutuhan
- Python 3.9+
- Pygame

## Instalasi
Di folder proyek ini, jalankan:

```bash
pip install -r requirements.txt
```

## Menjalankan
```bash
python main.py
```

## Kontrol
- Panah Kiri/Kanan/Atas/Bawah: Gerakkan Pacman
- R: Restart saat menang/kalah
- ESC: Keluar

## Catatan Teknis
- Grid: 32 kolom x 24 baris. Setiap tile 25px sehingga total 800x600
- Tile '4' (gate) hanya bisa dilalui hantu ketika keluar dari rumah (state `in_house = True`)
- Power mode (frightened) berlangsung selama 6 detik, hantu melambat dan berubah warna menjadi cyan
- Tabrakan menggunakan `rect` berbasis radius pada `Pacman` dan `Ghost`

## Troubleshooting
- Jika Pygame gagal membuka jendela pada beberapa environment (mis. server/headless), pastikan dijalankan di desktop Windows/macOS/Linux dengan dukungan tampilan (SDL)
- Jika `pip` menunjuk ke Python lain, gunakan `py -m pip install -r requirements.txt` dan `py main.py` di Windows

Selamat bermain!
