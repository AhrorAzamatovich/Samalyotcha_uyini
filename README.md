# ✈ Samalyotcha O'yini — Professional Edition

**Cheksiz davom etuvchi, qiyinlashib boradigan uyin** | by Ahrorazamatovich

---

## 🎮 O'yinni ishga tushirish

```bash
pip install pygame
python main.py
```

---

## 🌟 Yangi imkoniyatlar

### 🎨 Grafika
- Zamonaviy gradient samalyot rasmlari (faylsiz ham ishlaydi)
- Parallax harakatlanuvchi yo'l
- Yulduzli kosmik fon
- Portlash zarrachalari animatsiyasi
- Samalyot qiyalanish (tilt) animatsiyasi

### 🕹️ O'yin mexanikasi
- **3 ta jon tizimi** — har to'qnashuvda 1 jon ketadi
- **Qiyinlik darajalari**: Oson / O'rta / Qiyin
- **Zigzag dushmanlar** — Qiyin rejimda
- **Dushman o'qlari** — O'rta va Qiyin rejimda
- **Dushman HP** — Qiyin rejimda 2 ta HP
- **O'q otish** — SPACE tugmasi

### ⭐ Power-uplar (random tushadi)
| Power-up | Ta'sir | Davom etish |
|----------|--------|-------------|
| 🛡 Qalqon | To'qnashuvdan himoya | 5 soniya |
| ✦✦ Ikki o'q | Bir vaqtda 2 ta o'q | 6 soniya |
| ❄ Muzlatish | Dushmanlar sekinlashadi | 5 soniya |
| ❤ Qo'shimcha jon | +1 jon qo'shiladi | — |

### 🏆 Menyular
- **Asosiy menyu** — animatsiyali tugmalar, rekord ko'rsatkichi
- **Qiyinlik tanlash** — 3 daraja, tavsif bilan
- **Rekordlar taxtasi** — har bir qiyinlik uchun alohida
- **Sozlamalar** — ovoz yoqish/o'chirish
- **Pauza** — ESC tugmasi

### 🎵 Ovoz effektlari (sintetik, fayl shart emas)
- O'q otish tovushi
- Portlash tovushi
- Power-up yig'ish tovushi
- Zararlanish tovushi

### 📊 HUD (boshqaruv paneli)
- Ochko (yangilanganda yaltirashi)
- Jonlar (yurak belgisi bilan)
- Faol power-up va ularning vaqti
- Joriy tezlik
- Qiyinlik darajasi
- Xabarlar (pastki qism)

---

## ⌨️ Boshqaruv

| Tugma | Harakat |
|-------|---------|
| ← / A | Chapga harakat |
| → / D | O'ngga harakat |
| SPACE | O'q otish |
| ESC | Pauza |

---

## 📁 Fayl tuzilmasi

```
Samalyotcha_uyini/
├── main.py          # Asosiy o'yin kodi
├── 1.png            # O'yinchi samalyot rasmi (ixtiyoriy)
├── 3.png            # Dushman samalyot rasmi (ixtiyoriy)
├── highscores.json  # Rekordlar (avtomatik yaratiladi)
└── README.md
```

> **Eslatma:** `1.png` va `3.png` fayllari bo'lmasa ham, o'yin o'zi chizilgan grafika bilan ishlaydi.

---

## 🚀 Talab

- Python 3.8+
- pygame 2.x: `pip install pygame`
