# SavolJavob BOT

Qurilish sohasidagi ekspertga savol berish uchun Telegram bot.

## Imkoniyatlar

**Foydalanuvchilar:**
- Ekspertga savol yuborish (3 daqiqada 1 marta)
- Balansni to'ldirish (rasm yoki PDF chek yuborish orqali)
- Javob kelganda bildirishnoma olish
- Support bilan bog'lanish
- Til tanlash (O'zbek / Русский)

**Ekspertlar:**
- Savollarga javob berish va narx belgilash
- To'lovlarni tasdiqlash / rad etish
- Foydalanuvchilarni ban / unban qilish
- Statistikani ko'rish
- Barcha foydalanuvchilarga e'lon yuborish
- Karta raqami, egasi va support username ni sozlash

## Texnologiyalar

- Python 3.13
- [aiogram 3](https://docs.aiogram.dev/) — Telegram Bot framework
- SQLite + aiosqlite — ma'lumotlar bazasi
- Docker — deploy

## O'rnatish

### 1. Reponi clone qilish

```bash
git clone https://github.com/USERNAME/SavolJavobBOT.git
cd SavolJavobBOT
```

### 2. `.env` fayl yaratish

```bash
cp .env.example .env
```

`.env` ni tahrirlang:

```env
BOT_TOKEN=your_bot_token_here
EXPERT_IDS=123456789,987654321
DB_PATH=bot.db
```

- `BOT_TOKEN` — [@BotFather](https://t.me/BotFather) dan olingan token
- `EXPERT_IDS` — ekspert Telegram ID lari (vergul bilan ajratilgan)

### 3. Docker orqali ishga tushirish

```bash
docker compose up -d --build
```

Loglarni ko'rish:

```bash
docker compose logs -f
```

To'xtatish:

```bash
docker compose down
```

## Ma'lumotlar bazasi

DB fayli Docker volume da saqlanadi va konteyner qayta ishga tushganda o'chmaydi.

### Backup olish

```bash
docker compose cp bot:/app/data/bot.db ./bot_backup.db
```

### Avtomatik kunlik backup (cron)

```bash
crontab -e
```

```cron
0 3 * * * cd /path/to/SavolJavobBOT && mkdir -p backups && docker compose cp bot:/app/data/bot.db ./backups/bot_$(date +\%Y\%m\%d).db && find ./backups -name "bot_*.db" -mtime +7 -delete
```

## Loyiha tuzilmasi

```
SavolJavobBOT/
├── handlers/
│   ├── user/          # Foydalanuvchi handlerlari
│   └── expert/        # Ekspert handlerlari
├── database/
│   ├── db.py          # DB funksiyalari
│   └── models.py      # Modellar
├── keyboards/         # Tugmalar
├── locales/           # O'zbek va Rus tillari
├── middlewares/       # Til middleware
├── states/            # FSM holatlari
├── utils/             # Yordamchi funksiyalar
├── main.py
├── config.py
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```
