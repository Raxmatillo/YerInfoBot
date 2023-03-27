from typing import Union

from aiogram import types
from aiogram.types import CallbackQuery, Message

from data.config import ADMINS
from keyboards.inline.farm_keyboards import (
    menu_cd,
    district_keyboards,
    farm_keyboards,
    farmer_keyboards,
    one_farmer_keyboards,
)
from loader import dp, db



# Bosh menyu matni uchun handler
@dp.message_handler(text="Bosh menyu")
async def show_menu(message: types.Message):
    # Foydalanuvchilarga barcha kategoriyalarni qaytaramiz
    await list_districts(message)


# Kategoriyalarni qaytaruvchi funksiya. Callback query yoki Message qabul qilishi ham mumkin.
# **kwargs yordamida esa boshqa parametrlarni ham qabul qiladi: (district, farm, farmer)
async def list_districts(message: Union[CallbackQuery, Message], **kwargs):
    # Keyboardni chaqiramiz
    markup = await district_keyboards()

    # Agar foydalanuvchidan Message kelsa Keyboardni yuboramiz
    if isinstance(message, Message):
        await message.answer("Bo'lim tanlang", reply_markup=markup)

    # Agar foydalanuvchidan Callback kelsa Callback natbibi o'zgartiramiz
    elif isinstance(message, CallbackQuery):
        call = message
        await call.message.edit_reply_markup(markup)


# Ost-kategoriyalarni qaytaruvchi funksiya
async def list_farms(callback: CallbackQuery, district, **kwargs):
    markup = await farm_keyboards(district)

    # Xabar matnini o'zgartiramiz va keyboardni yuboramiz
    await callback.message.edit_reply_markup(markup)


# Ost-kategoriyaga tegishli mahsulotlar ro'yxatini yuboruvchi funksiya
async def list_farmers(callback: CallbackQuery, district, farm, **kwargs):
    markup = await farmer_keyboards(district, farm)
    print("hey")
    await callback.message.edit_text(text="Mahsulot tanlang", reply_markup=markup)


# Biror mahsulot uchun Xarid qilish tugmasini yuboruvchi funksiya
async def show_item(callback: CallbackQuery, district, farm, farmer):
    markup = one_farmer_keyboards(district, farm, farmer)
    print("Your user_id:", callback.message.from_user.id)
    if callback.message.from_user.id == ADMINS[0]:
        markup.row(
            types.InlineKeyboardButton(
                text="Yangilash",
                callback_data="update_excel"
            )
        )
    # Mahsulot haqida ma'lumotni bazadan olamiz
    item = await db.get_product(farmer)

    if item["photo"]:
        text = f"<a href=\"{item['photo']}\">{item['productname']}</a>\n\n"
    else:
        text = f"{item['productname']}\n\n"
    text += f"Narxi: {item['price']}$\n{item['description']}"

    await callback.message.edit_text(text=text, reply_markup=markup)


# Yuqoridagi barcha funksiyalar uchun yagona handler
@dp.callback_query_handler(menu_cd.filter())
async def navigate(call: CallbackQuery, callback_data: dict):
    """
    :param call: Handlerga kelgan Callback query
    :param callback_data: Tugma bosilganda kelgan ma'lumotlar
    """

    # Foydalanuvchi so'ragan Level (qavat)
    current_level = callback_data.get("level")

    # Foydalanuvchi so'ragan Kategoriya
    district = callback_data.get("district")

    # Ost-kategoriya (har doim ham bo'lavermaydi)
    farm = callback_data.get("farm")

    # Mahsulot ID raqami (har doim ham bo'lavermaydi)
    farmer = int(callback_data.get("farmer"))

    # Har bir Level (qavatga) mos funksiyalarni yozib chiqamiz
    levels = {
        "0": list_districts,  # Kategoriyalarni qaytaramiz
        "1": list_farms,  # Ost-kategoriyalarni qaytaramiz
        "2": list_farmers,  # Mahsulotlarni qaytaramiz
        "3": show_item,  # Mahsulotni ko'rsatamiz
    }

    # Foydalanuvchidan kelgan Level qiymatiga mos funksiyani chaqiramiz
    current_level_function = levels[current_level]

    # Tanlangan funksiyani chaqiramiz va kerakli parametrlarni uzatamiz
    await current_level_function(
        call, district=district, farm=farm, farmer=farmer
    )