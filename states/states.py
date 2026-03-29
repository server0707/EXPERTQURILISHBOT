from aiogram.fsm.state import State, StatesGroup


class UserState(StatesGroup):
    choosing_language = State()   # Til tanlash
    asking_question = State()     # Savol yozish
    entering_topup_amount = State()  # To'ldirish miqdori
    sending_check = State()          # Chek yuborish


class ExpertState(StatesGroup):
    writing_answer = State()      # Javob yozish (question_id saqlanadi)
    entering_price = State()      # Narx kiritish
    broadcasting = State()        # Reklama/e'lon yozish
    changing_card_number = State()       # Karta raqamini o'zgartirish
    changing_card_owner = State()        # Karta egasini o'zgartirish
    changing_support_username = State()  # Support username o'zgartirish
    banning_user = State()               # User ID kiritish (ban uchun)
    unbanning_user = State()             # User ID kiritish (unban uchun)
