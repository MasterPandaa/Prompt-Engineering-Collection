# Snake Game (Pygame)

Game Snake sederhana menggunakan Pygame.

## Fitur
- Layar 600x400 piksel, grid 20x20.
- Kontrol panah, tidak bisa berbalik arah 180°.
- Makanan muncul acak dan tidak menimpa tubuh ular.
- Ular bertambah panjang saat makan, skor bertambah.
- Game over saat menabrak dinding atau tubuh sendiri.
- Tampilan skor di kiri atas.

## Persyaratan
- Python 3.8+
- Pygame

## Instalasi
Di folder proyek ini:

```bash
pip install -r requirements.txt
```

Jika `pip` Anda adalah `pip3`:

```bash
pip3 install -r requirements.txt
```

## Menjalankan
```bash
python snake_game.py
```

## Kontrol
- Panah atas/bawah/kiri/kanan untuk menggerakkan ular.
- Saat Game Over: tekan `R` untuk restart, `Q` untuk keluar.

## Pengaturan Opsional
- Kecepatan game: ubah nilai `FPS` di `snake_game.py` (default 12; semakin besar semakin cepat).
- Grid bantu: di `snake_game.py`, aktifkan pemanggilan `draw_grid()` pada bagian render jika ingin menampilkan garis grid tipis.
