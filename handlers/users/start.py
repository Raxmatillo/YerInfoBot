import sqlite3

from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart

from data.config import ADMINS
from keyboards.default.menu import menu
from loader import dp, db, bot


@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    name = message.from_user.full_name
    # Foydalanuvchini bazaga qo'shamiz
    users = db.select_all_users()
    if str(message.from_user.id) not in str(users):
        try:
            db.add_user(
                full_name=name,
                username=message.from_user.username,
                telegram_id=message.from_user.id
            )
        except sqlite3.IntegrityError as err:
            await bot.send_message(chat_id=ADMINS[0], text=err)

    await message.answer("Хуш келибсиз!", reply_markup=menu)
