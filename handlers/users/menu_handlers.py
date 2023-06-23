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
from aiogram.dispatcher import FSMContext
from keyboards.inline.callback_data import district_callback, farm_callback, farmer_callback


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

    markup.add(
        types.InlineKeyboardButton(text="➕ Qo'shish", callback_data="district:add_item"),
        types.InlineKeyboardButton(text="➖ O'chirish", callback_data="district:del_item"),
    )

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
    markup.add(
        types.InlineKeyboardButton(text="➕ Qo'shish", callback_data=f"farm:add_item:{district}"),
        types.InlineKeyboardButton(text="➖ O'chirish", callback_data=f"farm:del_item:{district}"),
    )

    # Xabar matnini o'zgartiramiz va keyboardni yuboramiz
    await callback.message.edit_reply_markup(markup)


# Ost-kategoriyaga tegishli mahsulotlar ro'yxatini yuboruvchi funksiya
async def list_farmers(callback: CallbackQuery, district, farm, **kwargs):
    markup = await farmer_keyboards(district, farm)

    markup.add(
        types.InlineKeyboardButton(text="➕ Qo'shish", callback_data=f"farmer:add_item:{district}:{farm}"),
        types.InlineKeyboardButton(text="➖ O'chirish", callback_data=f"farmer:del_item:{district}:{farm}"),
    )


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






# district add and delete
@dp.callback_query_handler(district_callback.filter(item_name="add_item"))
async def add_district(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    await call.message.answer("Yangi tuman nomini yozing")
    await state.set_state("add_district")

@dp.message_handler(state="add_district")
async def add_district_to_db(message: types.Message, state: FSMContext):
    await message.answer(f"Tuman qabul qilindi, {message.text}")
    await state.finish()


@dp.callback_query_handler(district_callback.filter(item_name="del_item"))
async def del_district(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    markup = await district_keyboards(delete=True)
    markup.row(
        types.InlineKeyboardButton(text="⬅️ Ортга", callback_data="cancel_del_district")
    )
    await call.message.answer("Tumanni o'chirish", reply_markup=markup)
    await state.set_state("del_district")


@dp.callback_query_handler(menu_cd.filter(), state="del_district")
async def del_district_from_db(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    district_id = callback_data.get("district")
    district = db.get_district_one(id=district_id)[0][0]
    await call.answer(f"✅ {district} o'chirildi")
    await call.message.edit_reply_markup()
    await list_districts(message=call)
    await state.finish()

@dp.callback_query_handler(text="cancel_del_district", state="del_district")
async def cancel_delete_district(call: types.CallbackQuery, state: FSMContext):
    await list_districts(message=call)
    await state.finish()




# farm add and delete
@dp.callback_query_handler(farm_callback.filter(item_name="add_item"))
async def add_farm(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    await call.message.answer("Yangi ho'jalik nomini yozing")
    await state.set_state("add_farm")

@dp.message_handler(state="add_farm")
async def add_farm_to_db(message: types.Message, state: FSMContext):
    await message.answer(f"Ho'jalik qabul qilindi, {message.text}")
    await state.finish()


@dp.callback_query_handler(farm_callback.filter(item_name="del_item"))
async def del_farm(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    district_id = callback_data.get("item_id")
    await call.message.edit_reply_markup()
    markup = await farm_keyboards(district_id=district_id, delete=True)
    await call.message.answer("Ho'jalikni o'chirish", reply_markup=markup)
    await state.update_data(district_id = district_id)
    await state.set_state("del_farm")


@dp.callback_query_handler(menu_cd.filter(), state="del_farm")
async def del_farm_from_db(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    await call.message.edit_reply_markup()

    data = await state.get_data()

    district_id = data["district_id"]
    cancel = callback_data.get("cancel")
    if cancel == "farm_cancel":
        await list_farms(callback=call, district=district_id)
    else:
        farm_id = callback_data.get("farm")
        farm = db.get_farm_one(farm_id=farm_id)[0][0]
        await call.answer(f"✅ {farm} o'chirildi", cache_time=1)
        await list_farms(callback=call, district=district_id)
    await state.finish()

# farmer add and delete
@dp.callback_query_handler(farmer_callback.filter(item_name="add_item"))
async def add_farmer(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    await call.message.answer("Yangi fermer nomini yozing")
    await state.set_state("add_farmer")

@dp.message_handler(state="add_farmer")
async def add_farmer_to_db(message: types.Message, state: FSMContext):
    await message.answer(f"Fermer qabul qilindi, {message.text}")
    await state.finish()


@dp.callback_query_handler(farmer_callback.filter(item_name="del_item"))
async def del_farmer(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    district_id = callback_data.get("item_id")
    farm_id = callback_data.get("_item_id")
    farmer_id = callback_data.get("farmer_id")
    await call.message.edit_reply_markup()
    markup = await farmer_keyboards(district_id=district_id, farm_id=farm_id, delete=True)
    await call.message.answer("Fermerni o'chirish", reply_markup=markup)
    await state.update_data(farm_id=farm_id, district_id=district_id)
    await state.set_state("del_farmer")


@dp.callback_query_handler(menu_cd.filter(), state="del_farmer")
async def del_farmer_from_db(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    print(callback_data)
    data = await state.get_data()
    farm_id = data["farm_id"]
    district_id = data["district_id"]
    farmer_id = callback_data.get("farmer")

    print(f"farmer_id: {farmer_id}, farm_id: {farm_id}, district_id: {district_id}")
    cancel = callback_data.get("cancel")
    district_id = callback_data.get("district")

    if cancel == "farmer_cancel":
        print('yeo')
        await list_farmers(callback=call, district=district_id, farm=farm_id)
    else:
        farmer = db.get_farmer_one(farmer_id=farmer_id)[0][1]
        await call.answer(f"✅ {farmer} o'chirildi", cache_time=1)
        await list_farmers(callback=call, district=district_id, farm=farm_id)
    await state.finish()






# @dp.callback_query_handler(farmer_callback.filter(item_name="show_item"), state="del_farmer")
# async def cancel_del_farmer(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
#     await call.message.edit_reply_markup()



