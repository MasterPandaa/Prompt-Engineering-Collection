# Pacman Pygame (Simple)

Proyek ini adalah implementasi sederhana game Pacman menggunakan Pygame, berbasis grid sesuai contoh yang Anda berikan. Fitur:

- Render maze dari list 2D.
- Pacman bergerak dengan tombol panah, memakan pelet (2) dan power-pellet (3).
- 2 hantu dengan AI sederhana (bergerak acak di jalur yang tersedia).
- Logika tabrakan Pacman vs Hantu dan status power-up (hantu menjadi biru dan bergerak lebih lambat; Pacman dapat memakan hantu untuk skor tambahan).
- Menang saat semua pelet habis.

## Cara Menjalankan

1. Pastikan Python 3.9+ terpasang.
2. Instal dependensi:

```bash
pip install -r requirements.txt
```

3. Jalankan game:

```bash
python main.py
```

## Kontrol

- Panah Kiri/Kanan/Atas/Bawah: Gerakkan Pacman.
- R: Restart ketika menang/kalah.
- ESC: Keluar.

## Struktur Grid

- 1 = Dinding
- 0 = Jalur Kosong
- 2 = Pelet Kecil (+10 skor)
- 3 = Power Pellet (+50 skor, aktifkan mode POWER selama 6 detik)

## Catatan

- Kecepatan Pacman dan Hantu, ukuran tile, dan durasi power dapat diubah di bagian konfigurasi di `main.py`.
- Ukuran jendela diset otomatis berdasarkan ukuran grid dan `CELL_SIZE`.
