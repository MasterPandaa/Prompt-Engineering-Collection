# Pacman (Pygame)

Game Pacman sederhana berbasis Pygame. Menyertakan:
- Maze grid-based, pelet, power-pellet
- Pacman controllable (panah)
- 4 Ghost dengan AI sederhana (greedy ke pemain; frightened saat power-up)
- Manajemen state: skor, nyawa, power, win/lose

## Persyaratan
- Python 3.9+
- Pygame (lihat `requirements.txt`)

## Instalasi

```bash
pip install -r requirements.txt
```

Catatan Windows: jika ada kendala, coba:
```powershell
py -m pip install pygame==2.6.1
```

## Menjalankan

```bash
python main.py
```

Kontrol:
- Panah Atas/Bawah/Kiri/Kanan untuk bergerak
- ESC untuk keluar
- Enter/Space untuk restart setelah menang/kalah

## Struktur File
- `main.py` — kode game utama
- `requirements.txt` — dependensi
- `README.md` — panduan ini

## Catatan Teknis
- Peta (`MAZE_LAYOUT`) didefinisikan sebagai list string di `main.py`.
- Karakter: `#` dinding, `.` pelet, `o` power-pellet, `P` spawn Pacman, `G` spawn Ghost, spasi adalah jalan kosong.
- Ghost AI: saat di persimpangan memilih arah yang bukan kebalikan langkah sebelumnya dan tidak menabrak dinding; dalam mode normal memilih arah yang meminimalkan jarak Manhattan ke Pacman; dalam mode frightened bergerak acak.
- Tabrakan dan makan pelet diperiksa saat Pacman berada di pusat tile.
