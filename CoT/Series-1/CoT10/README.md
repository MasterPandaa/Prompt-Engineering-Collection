# Pong AI (Pygame)

Sebuah implementasi sederhana game Pong dengan AI menggunakan Pygame.

## Fitur
- Paddle pemain dikendalikan dengan W/S atau Arrow Up/Down
- Paddle AI otomatis mengikuti bola dengan toleransi agar tidak jitter
- Bola memantul pada dinding atas/bawah dan paddle, sudut pantul bervariasi
- Sistem skor otomatis saat bola keluar dari batas kiri/kanan

## Persyaratan
- Python 3.8+
- Pygame

## Instalasi
```bash
pip install -r requirements.txt
```

## Menjalankan
```bash
python pong_ai.py
```

## Kontrol
- W / Arrow Up: gerak ke atas
- S / Arrow Down: gerak ke bawah

## Catatan
- Jika jendela tidak muncul di atas, coba alt+tab atau jalankan dari terminal, bukan dari IDE yang menekan jendela grafis.
- Anda dapat menyesuaikan kesulitan dengan mengubah `AI_SPEED` dan `AI_TOLERANCE` di `pong_ai.py`.
