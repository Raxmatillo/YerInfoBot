import os
from typing import Union

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message

from data.config import ADMINS
from keyboards.inline.farm_keyboards import (
    menu_cd,
    district_keyboards,
    farm_keyboards,
    farmer_keyboards,
    one_farmer_keyboards,
)
from loader import dp, db, bot
from states.FarmerState import UpdateExcel

from utils.misc.my_functions import excel

# Bosh menyu matni uchun handler
@dp.message_handler(text="Туманлар")
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
        await message.answer("Бўлим танланг", reply_markup=markup)

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
    await callback.message.edit_text(text="Бўлим танланг",
                                     reply_markup=markup)


# Biror mahsulot uchun Xarid qilish tugmasini yuboruvchi funksiya
async def show_item(callback: CallbackQuery, district, farm, farmer):

    if callback.from_user.id == int(ADMINS[0]):
        markup = await one_farmer_keyboards(district_id=district,
                                            farm_id=farm, farmer_id=farmer,
                                            admin=True)
    else:
        markup = await one_farmer_keyboards(
            district_id=district,
            farm_id=farm,
            farmer_id=farmer
        )

    info = db.get_farmer_info(farmer_id=farmer)
    item = db.get_farmer_one(farmer_id=farmer)

    excels = sorted([x for x in os.listdir('download/excel')])
    file_path = ""
    for _excel in excels:
        if _excel.startswith(f"{district}-{farm}-{farmer}"):
            file_path = "download/excel/"+_excel
    await callback.message.edit_reply_markup()
    if item[0][-2] == None:
        await callback.message.answer(text="Бу бўлим ҳали тайёр эмас!",
                                      reply_markup=markup)
    else:
        info_excel = "<b>Контур - Фосфор | Калий | Gumus</b>\n\n"
        info_excel += excel(excel_file=file_path)
        await callback.message.answer_document(document=item[0][-2],
                                               caption="Excel fayl")
        if item[0][-1] != None:
            await callback.message.answer_document(document=item[0][-1],
                                               caption="Word fayl")
        await callback.message.answer(text=info_excel, reply_markup=markup,
                                      parse_mode='html')
        await callback.message.edit_text(text=f"{info[0][3]} / {info[0][2]} "
                                              f" / {info[0][1]}")


# @dp.callback_query_handler(menu_cd.filter(), state=UpdateExcel.go_state)
# async def unknown_cancel_button(call: CallbackQuery, state: FSMContext,
#                                 callback_data: dict):
#     current_level = callback_data.get("level")
#     if current_level == "3":
#         await state.finish()


# Yuqoridagi barcha funksiyalar uchun yagona handler
@dp.callback_query_handler(menu_cd.filter(), state=UpdateExcel.go_state)
@dp.callback_query_handler(menu_cd.filter())
async def navigate(call: CallbackQuery, callback_data: dict, state: FSMContext):
    """
    :param call: Handlerga kelgan Callback query
    :param callback_data: Tugma bosilganda kelgan ma'lumotlar
    """

    # Foydalanuvchi so'ragan Level (qavat)
    current_level = callback_data.get("level")

    #
    if current_level == "3":
        await state.finish()

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