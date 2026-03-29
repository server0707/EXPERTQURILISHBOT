import aiosqlite
from typing import Optional
from database.models import QuestionStatus, PaymentStatus


DB_PATH: str = "bot.db"


async def init_db(db_path: str = "bot.db"):
    global DB_PATH
    DB_PATH = db_path
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE NOT NULL,
                full_name TEXT NOT NULL,
                username TEXT,
                language TEXT DEFAULT 'uz',
                balance INTEGER DEFAULT 0,
                is_banned INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                text TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );

            CREATE TABLE IF NOT EXISTS answers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question_id INTEGER UNIQUE NOT NULL,
                expert_telegram_id INTEGER NOT NULL,
                text TEXT NOT NULL,
                price INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (question_id) REFERENCES questions(id)
            );

            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                amount INTEGER NOT NULL,
                check_file_id TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                expert_telegram_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );

            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                amount INTEGER NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );

            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );
        """)

        # Default sozlamalar
        await db.execute(
            "INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)",
            ("card_number", "0000 0000 0000 0000")
        )
        await db.execute(
            "INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)",
            ("card_owner", "Karta egasi")
        )
        await db.execute(
            "INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)",
            ("support_username", "")
        )
        await db.commit()

    # Mavjud DB uchun migration: is_banned ustuni
    async with aiosqlite.connect(DB_PATH) as db:
        try:
            await db.execute("ALTER TABLE users ADD COLUMN is_banned INTEGER DEFAULT 0")
            await db.commit()
        except Exception:
            pass  # Ustun allaqachon mavjud


# ─────────────────────────── USER ───────────────────────────

async def get_user(telegram_id: int) -> Optional[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM users WHERE telegram_id = ?", (telegram_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None


async def create_user(telegram_id: int, full_name: str, username: Optional[str], language: str = "uz"):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO users (telegram_id, full_name, username, language) VALUES (?, ?, ?, ?)",
            (telegram_id, full_name, username, language)
        )
        await db.commit()


async def update_user_language(telegram_id: int, language: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET language = ? WHERE telegram_id = ?",
            (language, telegram_id)
        )
        await db.commit()


async def get_balance(telegram_id: int) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT balance FROM users WHERE telegram_id = ?", (telegram_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 0


async def change_balance(telegram_id: int, amount: int, description: str) -> bool:
    """amount musbat = qo'shish, manfiy = ayirish.
    Manfiy holda balans 0 dan past ketmasligini tekshiradi. True = muvaffaqiyatli."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT id FROM users WHERE telegram_id = ?", (telegram_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if not row:
                return False
            user_id = row["id"]

        if amount < 0:
            # Faqat balans yetarli bo'lsa ayirish
            cursor = await db.execute(
                "UPDATE users SET balance = balance + ? WHERE telegram_id = ? AND balance + ? >= 0",
                (amount, telegram_id, amount)
            )
        else:
            cursor = await db.execute(
                "UPDATE users SET balance = balance + ? WHERE telegram_id = ?",
                (amount, telegram_id)
            )

        if cursor.rowcount == 0:
            await db.rollback()
            return False

        await db.execute(
            "INSERT INTO transactions (user_id, amount, description) VALUES (?, ?, ?)",
            (user_id, amount, description)
        )
        await db.commit()
        return True


async def get_all_user_telegram_ids() -> list[int]:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT telegram_id FROM users") as cursor:
            rows = await cursor.fetchall()
            return [row[0] for row in rows]


# ─────────────────────────── QUESTION ───────────────────────────

async def create_question(telegram_id: int, text: str) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT id FROM users WHERE telegram_id = ?", (telegram_id,)
        ) as cursor:
            row = await cursor.fetchone()
            user_id = row["id"]

        cursor = await db.execute(
            "INSERT INTO questions (user_id, text) VALUES (?, ?)",
            (user_id, text)
        )
        await db.commit()
        return cursor.lastrowid


async def get_question(question_id: int) -> Optional[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            """
            SELECT q.*, u.telegram_id as user_telegram_id, u.full_name, u.balance
            FROM questions q
            JOIN users u ON q.user_id = u.id
            WHERE q.id = ?
            """,
            (question_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None


async def update_question_status(question_id: int, status: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE questions SET status = ? WHERE id = ?",
            (status, question_id)
        )
        await db.commit()


async def get_pending_questions() -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            """
            SELECT q.*, u.telegram_id as user_telegram_id, u.full_name, u.username
            FROM questions q
            JOIN users u ON q.user_id = u.id
            WHERE q.status = ?
            ORDER BY q.created_at ASC
            """,
            (QuestionStatus.PENDING,)
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]


async def get_awaiting_payment_questions(telegram_id: int) -> list[dict]:
    """Foydalanuvchining to'lov kutayotgan savollari"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            """
            SELECT q.*, a.text as answer_text, a.price
            FROM questions q
            JOIN users u ON q.user_id = u.id
            JOIN answers a ON a.question_id = q.id
            WHERE q.status = ? AND u.telegram_id = ?
            ORDER BY q.created_at ASC
            """,
            (QuestionStatus.AWAITING_PAYMENT, telegram_id)
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]


# ─────────────────────────── ANSWER ───────────────────────────

async def create_answer(question_id: int, expert_telegram_id: int, text: str, price: int) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "INSERT INTO answers (question_id, expert_telegram_id, text, price) VALUES (?, ?, ?, ?)",
            (question_id, expert_telegram_id, text, price)
        )
        await db.commit()
        return cursor.lastrowid


async def get_answer_by_question(question_id: int) -> Optional[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM answers WHERE question_id = ?", (question_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None


# ─────────────────────────── PAYMENT ───────────────────────────

async def create_payment(telegram_id: int, amount: int, check_file_id: str) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT id FROM users WHERE telegram_id = ?", (telegram_id,)
        ) as cursor:
            row = await cursor.fetchone()
            user_id = row["id"]

        cursor = await db.execute(
            "INSERT INTO payments (user_id, amount, check_file_id) VALUES (?, ?, ?)",
            (user_id, amount, check_file_id)
        )
        await db.commit()
        return cursor.lastrowid


async def get_payment(payment_id: int) -> Optional[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            """
            SELECT p.*, u.telegram_id as user_telegram_id, u.full_name
            FROM payments p
            JOIN users u ON p.user_id = u.id
            WHERE p.id = ?
            """,
            (payment_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None


async def update_payment_status(payment_id: int, status: str, expert_telegram_id: int) -> bool:
    """Faqat PENDING holatdagi to'lovni yangilaydi. Muvaffaqiyatli bo'lsa True qaytaradi."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "UPDATE payments SET status = ?, expert_telegram_id = ? WHERE id = ? AND status = 'pending'",
            (status, expert_telegram_id, payment_id)
        )
        await db.commit()
        return cursor.rowcount > 0


# ─────────────────────────── SETTINGS ───────────────────────────

async def get_setting(key: str) -> Optional[str]:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT value FROM settings WHERE key = ?", (key,)
        ) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None


async def set_setting(key: str, value: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
            (key, value)
        )
        await db.commit()


# ─────────────────────────── BAN ───────────────────────────

async def ban_user(telegram_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET is_banned = 1 WHERE telegram_id = ?", (telegram_id,)
        )
        await db.commit()


async def unban_user(telegram_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET is_banned = 0 WHERE telegram_id = ?", (telegram_id,)
        )
        await db.commit()


async def is_user_banned(telegram_id: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT is_banned FROM users WHERE telegram_id = ?", (telegram_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return bool(row and row[0])


async def get_banned_users() -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT telegram_id, full_name, username FROM users WHERE is_banned = 1"
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]


# ─────────────────────────── RATE LIMIT ───────────────────────────

async def get_last_question_time(telegram_id: int) -> Optional[str]:
    """Foydalanuvchining oxirgi savol berish vaqtini qaytaradi (UTC ISO string)"""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            """
            SELECT MAX(q.created_at)
            FROM questions q
            JOIN users u ON q.user_id = u.id
            WHERE u.telegram_id = ?
            """,
            (telegram_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None


# ─────────────────────────── STATISTICS ───────────────────────────

async def get_statistics() -> dict:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM users") as c:
            total_users = (await c.fetchone())[0]
        async with db.execute("SELECT COUNT(*) FROM users WHERE is_banned = 1") as c:
            banned_users = (await c.fetchone())[0]
        async with db.execute("SELECT COUNT(*) FROM questions") as c:
            total_questions = (await c.fetchone())[0]
        async with db.execute(
            "SELECT COUNT(*) FROM questions WHERE status = ?", (QuestionStatus.PENDING,)
        ) as c:
            pending_questions = (await c.fetchone())[0]
        async with db.execute(
            "SELECT COUNT(*) FROM questions WHERE status = ?", (QuestionStatus.DELIVERED,)
        ) as c:
            delivered_questions = (await c.fetchone())[0]
        async with db.execute(
            "SELECT COUNT(*) FROM payments WHERE status = ?", (PaymentStatus.PENDING,)
        ) as c:
            pending_payments = (await c.fetchone())[0]
        async with db.execute(
            "SELECT COUNT(*), COALESCE(SUM(amount), 0) FROM payments WHERE status = ?",
            (PaymentStatus.CONFIRMED,)
        ) as c:
            row = await c.fetchone()
            confirmed_payments = row[0]
            total_topup = row[1]

    return {
        "total_users": total_users,
        "banned_users": banned_users,
        "total_questions": total_questions,
        "pending_questions": pending_questions,
        "delivered_questions": delivered_questions,
        "pending_payments": pending_payments,
        "confirmed_payments": confirmed_payments,
        "total_topup": total_topup,
    }
