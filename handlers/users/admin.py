import asyncio

from aiogram import types
from filters import AdminFilter

from data.config import ADMINS
from loader import dp, db, bot

from keyboards.inline.admin_keyboards import menu_keyboards

@dp.message_handler(AdminFilter(), text="/admin")
async def show_menu(message: types.Message):
    await message.answer("Adminpanel menyu", reply_markup=menu_keyboards)


@dp.callback_query_handler(AdminFilter(), text="districts")
async def show_districts(call: types.CallbackQuery):
    pass