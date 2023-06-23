from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


menu_keyboards = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Tumanlar", callback_data="districts")
        ]
    ], row_width=2
)