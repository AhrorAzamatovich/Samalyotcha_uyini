<div align="center">

# ✈ Samalyotcha O'yini
## Ultimate Professional Edition v3.0

**by Ahrorazamatovich**

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python)
![Pygame](https://img.shields.io/badge/Pygame-2.x-green?style=for-the-badge)
![Players](https://img.shields.io/badge/O'yinchilar-1%20yoki%202-orange?style=for-the-badge)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey?style=for-the-badge)

</div>

---

## 🚀 Tez ishga tushirish

```bash
pip install pygame
python main.py
```

---

## 👥 O'yinchi rejimlari

### 1 O'yinchi
| Tugma | Harakat |
|-------|---------|
| `← / A` | Chapga harakat |
| `→ / D` | O'ngga harakat |
| `SPACE` | O'q otish |
| `ESC` | Pauza |

### 2 O'yinchi (P1 + P2 birgalikda)
| O'yinchi | Boshqaruv | Harakat | O'q otish |
|----------|-----------|---------|-----------|
| **P1** | ⌨️ Klaviatura | `← / A` `→ / D` | `SPACE` |
| **P2** | 🖱️ Sichqoncha | Sichqoncha harakati | `LMB` (chap tugma) |

> 2 o'yinchi rejimida ekran ikkiga bo'linadi.
> P1 — chap zona, P2 — o'ng zona.
> Ikkovi birgalikda dushmanlarga qarshi kurashadi!

---

## 📦 Standalone EXE yaratish

> EXE faylni istalgan Windows kompyuterga ko'chiring — Python, pygame yoki boshqa hech narsa o'rnatish **KERAK EMAS**.

### Windows (1-usul: batch skript)
```
build.bat ni ikki marta bosing
```

### Yoki buyruq qatori (2-usul)
```bash
pip install pygame pyinstaller
python build.py
```

**Natija:** `dist/Samalyotcha/Samalyotcha.exe`

**Ko'chirish uchun:** `dist/Samalyotcha/` papkasini butunligicha ko'chiring.

---

## 🌟 Barcha imkoniyatlar

### 🕹️ O'yin mexanikasi

| Imkoniyat | Tavsif |
|-----------|--------|
| **1 / 2 o'yinchi** | Yakkaboshlik yoki do'st bilan birgalikda |
| **Wave tizimi** | Har 650 ballda yangi to'lqin (tezroq va ko'proq) |
| **Boss Battle** | Har 1000 ballda Boss keladi |
| **Boss — 3 faza** | Normal → Agressiv → QUTTIRIB |
| **Boss — 5 otish naqshi** | Spread, Triple, Aimed, Wave, Spiral |
| **Combo multiplier** | Ketma-ket o'ldirishda x1.1 ... bonus |
| **Screen Shake** | Portlash va zararda ekran titraydi |
| **3 ta jon** | Invincibility frames bilan |

### 👾 Dushman turlari

| Harakat turi | Tavsif |
|--------------|--------|
| **Straight** | To'g'ri pastga |
| **Zigzag** | Sinusoidal chapga-o'ngga |
| **Dive** | Tezlashib sho'ng'iydi |
| **Swoop** | Yoy bo'ylab |

### ⭐ 7 ta Power-up (random tushadi)

| Belgi | Tur | Effekt | Davomi |
|-------|-----|--------|--------|
| 🛡 | Shield | To'liq himoya | 6s |
| ⚡ | Double Shot | Ikki barobar o'q | 7s |
| ❄ | Slow | Dushmanlar 40% sekinlashadi | 5s |
| ♥ | Extra Life | +1 jon | — |
| 💣 | Nuke | Barcha dushmanlarni yo'q qiladi | — |
| 🚀 | Speed Up | 40% tezroq harakat | 5s |
| 🔥 | Laser | Vertikal laser nuri | 4s |

### 🎨 Grafika (hech qanday rasm fayli shart emas!)

- Protsessual gradient samalyot, dushman, boss grafikalari
- Portlash zarrachalari (Particle + Debris parchalar)
- Dvigatel tutuni animatsiyasi
- 3 qatlamli parallax yulduzlar (twinkle effekti)
- Screen shake (portlash va zararlanishda)
- Neon glow effektlari (Boss HP bar, power-up)
- Samalyot tilt (qiyalash) animatsiyasi
- CRT Scanlines rejimi (sozlamalarda)

### 🎵 Ovoz effektlari (sintetik, fayl shart emas!)

- Ambient lo-fi background musiqa (avtomatik loop)
- O'q, laser, portlash, katta portlash, boss gumburlashi
- Power-up, qalqon, nuke, level-up, combo, g'alaba SFX
- SFX va musiqa uchun alohida hajm slayderlar (sozlamalar)

### 🏆 Rekordlar

- Har qiyinlik uchun alohida rekord
- **COOP rekord** — 2 o'yinchi birgalikda
- Umumiy o'yinlar statistikasi
- JSON faylda saqlanadi (data/ papkasida)

### 🖥️ Menyular

| Ekran | Tavsif |
|-------|--------|
| **Splash ekrani** | Animatsiyali kirish sahifasi |
| **Asosiy menyu** | Rekord va qiyinlik ko'rsatkichi |
| **O'yinchi soni** | 1P yoki 2P tanlash + boshqaruv tavsifi |
| **Qiyinlik** | Easy / Medium / Hard |
| **Pauza** | ESC bilan, 3 tanlov |
| **Game Over** | Rekord animatsiyasi, havai o'tlar |
| **Rekordlar** | Har qiyinlik + COOP rekordi |
| **Sozlamalar** | Ovoz slayderlar, FPS, Scanlines, F11=Fullscreen |

---

## 🔧 Texnik tafsilotlar

```
main.py       — 1800 qator, barcha logika bitta faylda
                (standalone build uchun eng qulay arxitektura)
build.py      — PyInstaller avtomatik build skripti
build.bat     — Windows uchun bir bosish bilan build

O'yin loop:   60 FPS, double-buffered
Ekran:        1280 × 760 px
Ovoz:         44100 Hz, 16-bit stereo (sintetik)
Saqlash:      data/highscores.json, data/settings.json
EXE:          ~40-60 MB (pygame ichiga kiritilgan)
```

---

## 🛠️ Talab

**O'ynash uchun:**
- Python 3.8+
- `pip install pygame`

**EXE yaratish uchun:**
- `pip install pygame pyinstaller`
- `python build.py`

---

<div align="center">

**Ultimate Professional Edition — Professional dasturchilar ham hayratlanadigan darajada! 🚀**

*F11 — To'liq ekran rejimi*

</div>
