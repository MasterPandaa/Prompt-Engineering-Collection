# Pacman (Pygame)

Game Pacman sederhana berbasis Pygame dengan grid maze seperti contoh yang Anda berikan.

## Fitur
- Render maze dari list 2D (0=kosong, 1=dinding, 2=pelet, 3=power-pellet)
- Pacman bergerak dengan tombol panah
- Makan pelet dan power-pellet (mode power selama 7 detik)
- 2 hantu dengan AI sederhana (gerak acak), melambat saat frightened
- Logika tabrakan Pacman vs Hantu, skor, dan kondisi menang/kalah

## Persyaratan
- Python 3.8+
- Pygame

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

## Menjalankan

```bash
python main.py
```

## Kontrol
- Panah Atas/Bawah/Kiri/Kanan: Gerakkan Pacman
- R: Restart saat Game Over/Win

## Struktur
- `main.py`: Seluruh implementasi game (render, input, logika)
- `requirements.txt`: Dependensi Python

Selamat bermain!
