from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

user_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📋 Посмотреть услуги"), KeyboardButton(text="📝 Записаться в очередь")],
        [KeyboardButton(text="📅 Моя очередь")]
    ],
    resize_keyboard=True
)

def cancel_queue_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="❌ Отменить запись", callback_data="cancel_my_entry")]
        ]
    )
