# Pong dengan AI (Pygame)

Game Pong sederhana dengan AI menggunakan Pygame.

## Persyaratan
- Python 3.8+
- Pygame (lihat `requirements.txt`)

## Instalasi
```bash
python -m pip install -r requirements.txt
```

## Menjalankan
```bash
python pong_ai.py
```

## Kontrol
- W: Gerak ke atas
- S: Gerak ke bawah

## Fitur
- Layar 800x600
- Paddle pemain kiri (kontrol W/S)
- Paddle AI kanan mengikuti posisi Y bola dengan kecepatan maksimum
- Pantulan bola pada dinding dan paddle dengan sudut berdasarkan titik tumbukan
- Sistem skor dan jeda serve setelah gol
