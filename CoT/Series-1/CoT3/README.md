# Pong AI (Pygame)

Sebuah implementasi sederhana game Pong melawan AI menggunakan Pygame.

## Fitur
- Paddle pemain (kontrol: `W` untuk naik, `S` untuk turun)
- Paddle AI yang melacak posisi bola dengan deadzone agar tidak jitter
- Bola memantul dari dinding dan paddle, sudut pantul tergantung titik bentur
- Kecepatan bola meningkat sedikit tiap pantul, dibatasi `max_speed`
- Sistem skor dan countdown 3..2..1 setelah terjadi skor

## Persyaratan
- Python 3.8+
- Pygame

## Instalasi
```
pip install -r requirements.txt
```

## Menjalankan
```
python pong_ai.py
```

## Kontrol
- Pemain: `W` (naik), `S` (turun)
- AI bergerak otomatis

## Catatan
Jika jendela tidak muncul di atas, pastikan tidak ada error di terminal dan coba jalankan ulang perintah.
