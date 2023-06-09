from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Туманлар")
        ]
    ], resize_keyboard=True
)

empty_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="⚪️Бўш қолдириш")
        ],
    ], resize_keyboard=True
)


cancel_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Бекор қилиш")
        ],
    ], resize_keyboard=True
)
