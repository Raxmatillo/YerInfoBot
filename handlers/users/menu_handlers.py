import os
from typing import Union

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message

from filters import AdminFilter

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

    farmer_info = db.get_farmer_info(farmer_id=farmer)
            
    district_name = farmer_info[0][3]
    farm_name = farmer_info[0][2]
    farmer_name = farmer_info[0][1]
    farmer_file_name = farmer_info[0][5]

    try:
        file_path = f"download/excel/{district_name}/{farm_name}/{farmer_file_name}"
    except Exception as err:
        print(err, 'nomida xatolik')
    await callback.message.edit_reply_markup()
    if item[0][-3] == None:
        await callback.message.answer(text="Бу бўлим ҳали тайёр эмас!",
                                      reply_markup=markup)
    else:
        info_excel = "<b>Контур - Фосфор | Калий | Гумус</b>\n\n"
        info_excel += excel(excel_file=file_path)
        print(info_excel)
        await callback.message.answer_document(document=item[0][-3],
                                               caption="Excel fayl")

        await callback.message.answer(text=info_excel, reply_markup=markup,
                                      parse_mode='html')
        await callback.message.edit_text(text=f"{info[0][3]} / {info[0][2]} "
                                              f" / {info[0][1]}")




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
@dp.callback_query_handler(AdminFilter(), district_callback.filter(item_name="add_item"))
async def add_district(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    await call.message.answer("Yangi tuman nomini yozing")
    await state.set_state("add_district")

@dp.message_handler(AdminFilter(), state="add_district")
async def add_district_to_db(message: types.Message, state: FSMContext):
    await message.answer(f"Туман қабул қилинди, <b>{message.text}</b>", parse_mode='html')
    try:
        db.add_district(name=message.text)
        await list_districts(message=message)
    except Exception as err:
        await message.answer("Хатолик юз берди!")
    await state.finish()


@dp.callback_query_handler(AdminFilter(), district_callback.filter(item_name="del_item"))
async def del_district(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    markup = await district_keyboards(delete=True)
    markup.row(
        types.InlineKeyboardButton(text="⬅️ Ортга", callback_data="cancel_del_district")
    )
    await call.message.answer("Бўлим танланг", reply_markup=markup)
    await state.set_state("del_district")


@dp.callback_query_handler(AdminFilter(), menu_cd.filter(), state="del_district")
async def del_district_from_db(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    district_id = callback_data.get("district")
    district = db.get_district_one(id=district_id)
    try:
        db.delete_district(id=district_id)
        await call.answer(f"✅ {district[0][0]} ўчирилди")
        await call.message.edit_reply_markup()
        await list_districts(message=call)
        await state.finish()
    except Exception as err:
        print("Tuman o'chirishda xatolik", err)
        await call.message.answer("Хатолик юз берди!")

@dp.callback_query_handler(AdminFilter(), text="cancel_del_district", state="del_district")
async def cancel_delete_district(call: types.CallbackQuery, state: FSMContext):
    await list_districts(message=call)
    await state.finish()




# farm add and delete
@dp.callback_query_handler(AdminFilter(), farm_callback.filter(item_name="add_item"))
async def add_farm(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    await call.message.edit_reply_markup()
    await call.message.answer("Янги ҳўжалик номини ёзинг")
    await state.set_state("add_farm")
    await state.update_data(district=callback_data.get("item_id"))

@dp.message_handler(AdminFilter(), state="add_farm")
async def add_farm_to_db(message: types.Message, state: FSMContext):
    data = await state.get_data()
    district = data["district"]
    try:
        db.add_farm(name=message.text, district=district)
        markup = await farm_keyboards(district)
        markup.add(
            types.InlineKeyboardButton(text="➕ Қўшиш", callback_data=f"farm:add_item:{district}"),
            types.InlineKeyboardButton(text="➖ Ўчириш", callback_data=f"farm:del_item:{district}"),
        )
        await message.answer(f"Ҳўжалик қабул қилинди, <b>{message.text}</b>", reply_markup=markup, parse_mode='html')
        await state.finish()
    except Exception as err:
        print(err)
        await message.answer("Хатолик юз берди!")


@dp.callback_query_handler(AdminFilter(), farm_callback.filter(item_name="del_item"))
async def del_farm(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    district_id = callback_data.get("item_id")
    await call.message.edit_reply_markup()
    markup = await farm_keyboards(district_id=district_id, delete=True)
    await call.message.answer("Бўлим танланг", reply_markup=markup)
    await state.update_data(district_id = district_id)
    await state.set_state("del_farm")


@dp.callback_query_handler(AdminFilter(), menu_cd.filter(), state="del_farm")
async def del_farm_from_db(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    await call.message.edit_reply_markup()

    data = await state.get_data()

    district_id = data["district_id"]
    cancel = callback_data.get("cancel")
    if cancel == "farm_cancel":
        await list_farms(callback=call, district=district_id)
    else:
        try:
            farm_id = callback_data.get("farm")
            farm = db.get_farm_one(farm_id=farm_id)[0][0]
            print(farm_id)
            db.delete_farm(id=farm_id)
            await call.answer(f"✅ {farm} ўчирилди", cache_time=1)
            await list_farms(callback=call, district=district_id)
        except Exception as err:
            print("Farm o'chirishda xatolik", err)
        finally:
            await state.finish()




# farmer add and delete
@dp.callback_query_handler(AdminFilter(), farmer_callback.filter(item_name="add_item"))
async def add_farmer(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    await call.message.edit_reply_markup()
    await call.message.answer("Янги фермер номини ёзинг")
    district = callback_data.get('item_id')
    farm = callback_data.get("_item_id")
    await state.set_state("add_farmer")
    print(callback_data)
    await state.update_data(AdminFilter(), district=district, farm=farm)


@dp.message_handler(AdminFilter(), state="add_farmer")
async def add_farmer_to_db(message: types.Message, state: FSMContext):
    data = await state.get_data()
    district = data["district"]
    farm = data["farm"]
    try:
        db.add_farmer(AdminFilter(), name=message.text, farm=farm)
        markup = await farmer_keyboards(district, farm)

        markup.add(
            types.InlineKeyboardButton(text="➕ Қўшиш", callback_data=f"farmer:add_item:{district}:{farm}"),
            types.InlineKeyboardButton(text="➖ Ўчириш", callback_data=f"farmer:del_item:{district}:{farm}"),
        )

        await message.answer(text="Фермер қабул қилинди",
                                        reply_markup=markup)
        await state.finish()
    except Exception as err:
        print('add farmerda xatolik', err)
    farmer_info = db.get_farm_info(farm_id=farm)

    district_name = farmer_info[0][3]
    farm_name = farmer_info[0][2]   

    path_district = f"download/excel/{district_name}" if os.path.exists(f"download/excel/{district_name}") else os.mkdir(f"download/excel/{district_name}")

    mode = 0o666
    path = os.path.join(str(path_district), farm_name)
    os.mkdir(path, mode)



@dp.callback_query_handler(AdminFilter(), farmer_callback.filter(item_name="del_item"))
async def del_farmer(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    district_id = callback_data.get("item_id")
    farm_id = callback_data.get("_item_id")
    farmer_id = callback_data.get("farmer_id")
    await call.message.edit_reply_markup()
    markup = await farmer_keyboards(district_id=district_id, farm_id=farm_id, delete=True)
    await call.message.answer("Бўлим танланг", reply_markup=markup)
    await state.update_data(farm_id=farm_id, district_id=district_id)
    await state.set_state("del_farmer")


@dp.callback_query_handler(AdminFilter(), menu_cd.filter(), state="del_farmer")
async def del_farmer_from_db(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    data = await state.get_data()
    farm_id = data["farm_id"]
    district_id = data["district_id"]
    farmer_id = callback_data.get("farmer")

    cancel = callback_data.get("cancel")
    district_id = callback_data.get("district")

    if cancel == "farmer_cancel":
        await list_farmers(callback=call, district=district_id, farm=farm_id)
    else:
        try:
            farmer = db.get_farmer_one(farmer_id=farmer_id)[0][1]
            
            farmer_info = db.get_farmer_info(farmer_id=farmer_id)
            district_name = farmer_info[0][3]
            farm_name = farmer_info[0][2]
            file_name = farmer_info[0][5]
            file_path = f"download/excel/{district_name}/{farm_name}/{file_name}"
           
            if os.path.exists(file_path):
                os.remove(file_path)
                print("File deleted successfully.")
            else:
                print("File not found.")

            db.delete_farmer(id=farmer_id)
            await call.answer(f"✅ {farmer} ўчирилди", cache_time=1)
            await list_farmers(callback=call, district=district_id, farm=farm_id)
        except Exception as err:
            print("Farmer o'chirishda xatolik", err)
        finally:
            await state.finish()