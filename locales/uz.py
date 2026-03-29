texts = {
    # START
    "choose_language": "Tilni tanlang / Выберите язык:",
    "welcome": (
        "👋 Salom, {name}!\n\n"
        "Bu bot orqali qurilish sohasidagi ekspertga savol berishingiz mumkin.\n\n"
        "💡 Har bir savol uchun to'lov hisobingizdan yechiladi.\n"
        "💰 Joriy balansingiz: <b>{balance:,} so'm</b>"
    ),

    # MAIN MENU
    "main_menu": "Asosiy menyu:",
    "btn_ask": "❓ Savol berish",
    "btn_balance": "💰 Balans",
    "btn_topup": "💳 Balansni to'ldirish",
    "btn_cancel": "❌ Bekor qilish",
    "btn_back": "⬅️ Orqaga",
    "btn_language": "🌐 Tilni o'zgartirish",
    "choose_new_language": "🌐 Yangi tilni tanlang:",
    "btn_support": "📞 Support",
    "support_info": "📞 <b>Support bilan bog'lanish</b>\n\nQuyidagi manzilga yozing:\n{contact}",
    "support_not_set": "📞 Support hozircha sozlanmagan. Keyinroq urinib ko'ring.",

    # QUESTION
    "ask_question": (
        "✍️ Savolingizni yozing:\n\n"
        "<i>Bitta xabarda bir yoki bir nechta savol berish mumkin.</i>"
    ),
    "question_sent": (
        "✅ Savolingiz qabul qilindi! (#<b>{question_id}</b>)\n\n"
        "Ekspert tez orada javob beradi. Javob kelgach xabar olasiz."
    ),
    "question_cancelled": "❌ Bekor qilindi.",

    # BALANCE
    "balance_info": (
        "💰 <b>Balansingiz</b>\n\n"
        "Mavjud: <b>{balance:,} so'm</b>"
    ),

    # TOP UP
    "enter_topup_amount": "💳 Qancha so'm to'ldirmoqchisiz? (faqat raqam kiriting):",
    "invalid_amount": "❗ Noto'g'ri miqdor. Faqat musbat raqam kiriting:",
    "send_check": (
        "📋 To'lov ma'lumotlari:\n\n"
        "💳 Karta raqami: <code>{card_number}</code>\n"
        "👤 Karta egasi: <b>{card_owner}</b>\n"
        "💰 Miqdor: <b>{amount:,} so'm</b>\n\n"
        "To'lovni amalga oshirib, chek (screenshot yoki foto) yuboring:"
    ),
    "check_sent": (
        "✅ Chekingiz qabul qilindi!\n\n"
        "Ekspert tasdiqlashidan so'ng balans avtomatik to'ldiriladi."
    ),
    "topup_confirmed": (
        "✅ To'lovingiz tasdiqlandi!\n\n"
        "💰 Balansga qo'shildi: <b>{amount:,} so'm</b>\n"
        "💰 Joriy balans: <b>{balance:,} so'm</b>"
    ),
    "topup_rejected": (
        "❌ Afsuski, to'lovingiz tasdiqlanmadi.\n\n"
        "Noto'g'ri chek yoki miqdor bo'lishi mumkin. "
        "Qayta urinib ko'ring yoki ekspert bilan bog'laning."
    ),

    # ANSWER DELIVERY
    "answer_delivered": (
        "💬 <b>Savolingizga javob!</b> (#{question_id})\n\n"
        "<b>Savol:</b> {question_text}\n\n"
        "<b>Javob:</b>\n{answer_text}\n\n"
        "💰 Hisobingizdan yechildi: <b>{price:,} so'm</b>\n"
        "💰 Qolgan balans: <b>{balance:,} so'm</b>"
    ),
    "answer_free": (
        "💬 <b>Savolingizga javob!</b> (#{question_id})\n\n"
        "<b>Savol:</b> {question_text}\n\n"
        "<b>Javob:</b>\n{answer_text}\n\n"
        "✅ Bu javob bepul!"
    ),
    "answer_awaiting_payment": (
        "💬 <b>Savolingizga javob tayyor!</b> (#{question_id})\n\n"
        "💰 Javob narxi: <b>{price:,} so'm</b>\n"
        "💳 Balansingiz: <b>{balance:,} so'm</b>\n"
        "❗ Yetishmaydi: <b>{deficit:,} so'm</b>\n\n"
        "Balansni to'ldirgach, javob avtomatik yetkaziladi."
    ),
}
