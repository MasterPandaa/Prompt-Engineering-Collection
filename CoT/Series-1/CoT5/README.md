# Pong AI (Pygame)

Game Pong sederhana dengan satu pemain (kontrol W/S) melawan AI. Dibuat menggunakan Pygame.

## Fitur
- Kontrol pemain: tombol `W` (naik) dan `S` (turun)
- AI paddle mengikuti posisi Y bola dengan kecepatan terbatas (punya dead zone agar tidak jitter)
- Pantulan bola pada dinding dan paddle dengan sudut berdasarkan titik tabrak
- Sistem skor (bola reset ke tengah saat ada yang kebobolan)

## Persyaratan
- Python 3.8+
- Pygame (lihat `requirements.txt`)

## Instalasi
Disarankan membuat virtual environment (opsional tetapi direkomendasikan):

### PowerShell (Windows)
```powershell
# (Opsional) Buat dan aktifkan virtual env
py -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependensi
pip install -r requirements.txt
```

## Menjalankan
```powershell
python main.py
```

Jika jendela game tidak muncul atau terjadi error terkait Pygame, pastikan instalasi berhasil dan kartu grafis/driver Anda mendukung konteks video.

## Kontrol
- W: Paddle naik
- S: Paddle turun
- Tutup jendela: Keluar dari permainan

## Struktur
```
iterasi5/
├─ main.py            # Kode utama game
├─ requirements.txt   # Dependensi (pygame)
└─ README.md          # Panduan
```

## Penyesuaian Cepat
- Ubah ukuran layar: `WIDTH`, `HEIGHT`
- Kecepatan: `PLAYER_SPEED`, `AI_SPEED`, `BALL_SPEED`
- Ukuran paddle/bola: `PADDLE_W`, `PADDLE_H`, `BALL_SIZE`

Selamat bermain!
