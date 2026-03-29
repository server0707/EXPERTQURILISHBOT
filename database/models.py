from dataclasses import dataclass
from typing import Optional


# Question statuses
class QuestionStatus:
    PENDING = "pending"                   # Ekspert javob kutilmoqda
    ANSWERED = "answered"                 # Ekspert javob berdi, balans yetarli
    AWAITING_PAYMENT = "awaiting_payment" # Javob bor, balans yetarli emas
    DELIVERED = "delivered"               # Javob yetkazildi
    FREE = "free"                         # Bepul, yetkazildi


# Payment statuses
class PaymentStatus:
    PENDING = "pending"       # Chek yuborildi, tasdiq kutilmoqda
    CONFIRMED = "confirmed"   # Tasdiqlandi
    REJECTED = "rejected"     # Rad etildi


@dataclass
class User:
    id: int
    telegram_id: int
    full_name: str
    username: Optional[str]
    language: str          # "uz" yoki "ru"
    balance: int           # so'mda
    created_at: str


@dataclass
class Question:
    id: int
    user_id: int
    text: str
    status: str            # QuestionStatus
    created_at: str


@dataclass
class Answer:
    id: int
    question_id: int
    expert_telegram_id: int
    text: str
    price: int             # 0 = bepul
    created_at: str


@dataclass
class Payment:
    id: int
    user_id: int
    amount: int
    check_file_id: str     # Telegram file_id
    status: str            # PaymentStatus
    expert_telegram_id: Optional[int]
    created_at: str


@dataclass
class Transaction:
    id: int
    user_id: int
    amount: int            # musbat = kirim, manfiy = chiqim
    description: str
    created_at: str


@dataclass
class Setting:
    key: str
    value: str
