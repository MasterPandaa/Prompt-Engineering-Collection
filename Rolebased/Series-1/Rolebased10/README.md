# Pong (Pygame)

Implementasi game Pong yang bersih, efisien, dan mudah dibaca menggunakan Pygame.

## Fitur

- Layar 800x600 dengan 60 FPS.
- OOP: class `Paddle`, `AIPaddle`, dan `Ball` terorganisir rapi.
- Kontrol pemain: `W` (naik) dan `S` (turun).
- AI lawan: menantang namun adil (prediksi dengan reaction delay, error margin, dan smoothing).
- Fisika: pantulan akurat, peningkatan kecepatan bola bertahap, sistem skor, garis tengah, HUD.
- Kondisi menang: skor hingga 11.

## Persyaratan

 - Python 3.10+ (kode memakai tipe hint modern seperti PEP 604 `A | B`).
 - Pygame (lihat `requirements.txt`).

## Instalasi

Pada Windows (Command Prompt atau PowerShell):

```
py -m pip install -r requirements.txt
```

Jika Anda ingin memakai virtualenv:

```
py -m venv .venv
.venv\Scripts\activate
py -m pip install -r requirements.txt
```

## Menjalankan

```
py main.py
```

## Kontrol

- W: gerakkan paddle kiri ke atas.
- S: gerakkan paddle kiri ke bawah.
- ESC: keluar permainan.
- R: restart setelah ada pemenang.

## Struktur Kode Singkat

- `main.py`: seluruh implementasi permainan.
  - `Paddle`: paddle pemain kiri, handle input dan clamping layar.
  - `AIPaddle`: turunan `Paddle` dengan logika AI (prediksi, delay, jitter, smoothing).
  - `Ball`: posisi, kecepatan, pantulan dinding dan paddle, reset, dan cooldown serve.
  - `Game`: loop utama, update/draw, skor, HUD, restart.

## Catatan Desain

- Kecepatan bola meningkat sedikit pada setiap pantulan paddle dan setelah skor untuk meningkatkan tensi permainan, dibatasi `BALL_SPEED_MAX` agar tetap playable.
- AI memprediksi posisi bola saat mencapai sisi kanan termasuk pantulan dinding, tetapi diberi `reaction_delay`, `error_margin`, dan `track_smooth` agar bisa dikalahkan.
- Kode mengikuti PEP 8 dan memakai tipe hint serta `dataclass` untuk batas layar.
