
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
from aiogram.dispatcher import FSMContext

from loader import dp, db
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
        if str(message.from_user.id) in ADMINS:
             markup.add(
                types.InlineKeyboardButton(text="➕ Қўшиш", callback_data="district:add_item"),
                types.InlineKeyboardButton(text="➖ Ўчириш", callback_data="district:del_item"),
            )
        await message.answer("Бўлим танланг", reply_markup=markup)

    # Agar foydalanuvchidan Callback kelsa Callback natbibi o'zgartiramiz
    elif isinstance(message, CallbackQuery):
        call = message
        if str(call.from_user.id) in ADMINS:
             markup.add(
                types.InlineKeyboardButton(text="➕ Қўшиш", callback_data="district:add_item"),
                types.InlineKeyboardButton(text="➖ Ўчириш", callback_data="district:del_item"),
            )
        await call.message.edit_reply_markup(markup)


# Ost-kategoriyalarni qaytaruvchi funksiya
async def list_farms(callback: CallbackQuery, district, **kwargs):
    markup = await farm_keyboards(district)

    if str(callback.from_user.id) not in ADMINS:
        if len(markup.inline_keyboard) <=1:
            await callback.answer("Ho'jaliklar mavjud emas", show_alert=True)
            return
        
    if str(callback.from_user.id) in ADMINS:
        markup.add(
            types.InlineKeyboardButton(text="➕ Қўшиш", callback_data=f"farm:add_item:{district}"),
            types.InlineKeyboardButton(text="➖ Ўчириш", callback_data=f"farm:del_item:{district}"),
        )
    # Xabar matnini o'zgartiramiz va keyboardni yuboramiz
    await callback.message.edit_reply_markup(markup)


# Ost-kategoriyaga tegishli mahsulotlar ro'yxatini yuboruvchi funksiya
async def list_farmers(callback: CallbackQuery, district, farm, **kwargs):
    markup = await farmer_keyboards(district, farm)

    if str(callback.from_user.id) not in ADMINS:
        if len(markup.inline_keyboard) <=1:
            await callback.answer("Fermerlar mavjud emas", show_alert=True)
            return
        
    if str(callback.from_user.id) in ADMINS:
        markup.add(
            types.InlineKeyboardButton(text="➕ Қўшиш", callback_data=f"farmer:add_item:{district}:{farm}"),
            types.InlineKeyboardButton(text="➖ Ўчириш", callback_data=f"farmer:del_item:{district}:{farm}"),
        )

    await callback.message.edit_text(text="Бўлим танланг",
                                     reply_markup=markup)


# Biror mahsulot uchun Xarid qilish tugmasini yuboruvchi funksiya
async def show_item(callback: CallbackQuery, district, farm, farmer):

    if callback.from_user.id == int(ADMINS[0]):
        markup = await one_farmer_keyboards(district_id=district,
                                            farm_id=farm,
                                            farmer_id=farmer,
                                            admin=True)
    else:
        markup = await one_farmer_keyboards(
            district_id=district,
            farm_id=farm,
            farmer_id=farmer
        )

    info = db.get_farmer_info(farmer_id=farmer)
    item = db.get_farmer_one(farmer_id=farmer)

    farmer_info = db.get_farmer_info(farmer_id=farmer)
    print(farmer_info)
    district_name = farmer_info[0][3]
    farm_name = farmer_info[0][2]
    farmer_file_name = farmer_info[0][5]

    try:
        file_path = f"download/excel/{district_name}/{farm_name}/{farmer_file_name}"
    except Exception as err:
        print(err, 'nomida xatolik')
    await callback.message.edit_reply_markup()

    if item[0][3] and item[0][4]:
        await callback.message.answer_document(document=item[0][4], caption="Fayl")
        info_excel = "<b>Контур - Фосфор | Калий | Гумус</b>\n\n"
        info_excel += excel(excel_file=file_path)
        await callback.message.answer_document(document=item[0][3],
                                               caption="Excel fayl")

        await callback.message.answer(text=info_excel, reply_markup=markup,
                                      parse_mode='html')
        await callback.message.edit_text(text=f"{info[0][3]} / {info[0][2]} "
                                              f" / {info[0][1]}")
    else:
        if item[0][4] is not None:
            await callback.message.answer_document(document=item[0][4], caption="Fayl")
            await callback.message.edit_text(text=f"{info[0][3]} / {info[0][2]} "
                                                f" / {info[0][1]}")
            await callback.message.answer("Меню", reply_markup=markup)
        elif item[0][3] is not None:
            info_excel = "<b>Контур - Фосфор | Калий | Гумус</b>\n\n"
            info_excel += excel(excel_file=file_path)
            await callback.message.answer_document(document=item[0][3],
                                                caption="Excel fayl")

            await callback.message.answer(text=info_excel, reply_markup=markup,
                                        parse_mode='html')
            await callback.message.edit_text(text=f"{info[0][3]} / {info[0][2]} "
                                                f" / {info[0][1]}")
        else:
            await callback.message.answer(text="Бу бўлим ҳали тайёр эмас!",
                                      reply_markup=markup)


# Yuqoridagi barcha funksiyalar uchun yagona handler
@dp.callback_query_handler(menu_cd.filter(), state=UpdateExcel.go_state)
@dp.callback_query_handler(menu_cd.filter())
async def navigate(call: CallbackQuery, callback_data: dict, state: FSMContext):
    current_level = callback_data.get("level")

    if current_level == "3":
        await state.finish()

    district = callback_data.get("district")

    farm = callback_data.get("farm")

    farmer = int(callback_data.get("farmer"))

    levels = {
        "0": list_districts,
        "1": list_farms,
        "2": list_farmers,
        "3": show_item,
    }

    current_level_function = levels[current_level]

    await current_level_function(
        call, district=district, farm=farm, farmer=farmer
    )