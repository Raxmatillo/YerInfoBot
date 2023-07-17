import os
import shutil

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery
from aiogram.dispatcher import FSMContext
from filters import AdminFilter

from keyboards.inline.farm_keyboards import (
    menu_cd,
    district_keyboards,
    farm_keyboards,
    farmer_keyboards,
)
from keyboards.inline.callback_data import district_callback, farm_callback, farmer_callback
from keyboards.inline.farm_keyboards import yes_no_keyboards

from loader import dp, db

from .menu_handlers import list_districts, list_farmers, list_farms, show_item


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
    markup = await district_keyboards(delete=True)
    markup.row(
        types.InlineKeyboardButton(text="⬅️ Ортга", callback_data="cancel_del_district")
    )
    # await call.message.answer("
    await call.message.edit_reply_markup(markup)
    await state.set_state("del_district")


@dp.callback_query_handler(AdminFilter(), menu_cd.filter(), state="del_district")
async def delete_district_request(call: types.CallbackQuery, callback_data: dict, state:FSMContext):
    markup = await yes_no_keyboards()
    district_id = callback_data.get("district")
    await state.update_data(district_id=district_id)
    await call.message.edit_reply_markup()
    await call.message.answer("Rostan o'chirasizmi ?", reply_markup=markup)
    await state.set_state("confirm")


@dp.callback_query_handler(AdminFilter(), state="confirm", text="no_keyboard")
async def del_district_from_db_cancel(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text('Бўлим танланг')
    await list_districts(call)
    await state.finish()


@dp.callback_query_handler(AdminFilter(), state="confirm", text="yes_keyboard")
async def del_district_from_db(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    district_id = data.get("district_id")
    district = db.get_district_one(id=district_id)
    try:
        db.delete_district(id=district_id)
        await call.answer(f"✅ {district[0][0]} ўчирилди")
        await call.message.edit_text("Бўлим танланг")
        excel_dir = "download\excel\\"
        word_dir = "download\word\\"
        if os.path.exists(excel_dir+district[0][0]):
            shutil.rmtree(excel_dir+district[0][0])

        if os.path.exists(word_dir+district[0][0]):
            shutil.rmtree(word_dir+district[0][0])
            
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
    markup = await farm_keyboards(district_id=district_id, delete=True)
    await call.message.edit_reply_markup()
    await call.message.answer("Бўлим танланг", reply_markup=markup)
    await state.update_data(district_id = district_id)
    await state.set_state("del_farm")


@dp.callback_query_handler(AdminFilter(), menu_cd.filter(), state="del_farm")
async def delete_district_request(call: types.CallbackQuery, callback_data: dict, state:FSMContext):
    markup = await yes_no_keyboards()
    district_id = callback_data.get("district")
    farm_id = callback_data.get("farm")
    await state.update_data(district_id=district_id, farm_id=farm_id)
    await call.message.edit_text("Rostan o'chirasizmi ?")
    await call.message.edit_reply_markup(markup)
    await state.set_state("confirm_farm")


@dp.callback_query_handler(AdminFilter(), state="confirm_farm", text="no_keyboard")
async def del_district_from_db_cancel(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text('Бўлим танланг')
    data = await state.get_data()
    district = data.get("district_id")
    await list_farms(call, district)
    await state.finish()



@dp.callback_query_handler(AdminFilter(), state="confirm_farm", text="yes_keyboard")
async def del_farm_from_db(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    district_id = data["district_id"]
    try:
        farm_id = data.get("farm_id")
        farm = db.get_farm_one(farm_id=farm_id)[0][0]
        
        farm_info = db.get_farm_info(farm_id=farm_id)
        print('farm info', farm_info)
        district_name = farm_info[0][3]
        farm_name = farm_info[0][2]

        excel_dir = f"download\excel\\"+district_name+"\\"
        word_dir = f"download\word\\"+district_name+"\\"



        await call.answer(f"✅ {farm} ўчирилди", cache_time=1)
        await call.message.edit_text("Бўлим танланг")

        if os.path.exists(excel_dir+farm_name):
            shutil.rmtree(excel_dir+farm_name)
        if os.path.exists(word_dir+farm_name):
            shutil.rmtree(word_dir+farm_name)

        db.delete_farm(id=farm_id)

        await list_farms(callback=call, district=district_id)
    except Exception as err:
        print("Farm o'chirishda xatolik")
    finally:
        await state.finish()


# farmer add and delete
@dp.callback_query_handler(AdminFilter(), farmer_callback.filter(item_name="add_item"))
async def add_farmer(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    await call.message.edit_reply_markup()
    await call.message.answer("Янги фермер номини ёзинг")
    district = callback_data.get('item_id')
    farm = callback_data.get("_item_id")
    await state.update_data(district=district, farm=farm)
    await state.set_state("add_farmer")


@dp.message_handler(AdminFilter(), state="add_farmer")
async def add_farmer_to_db(message: types.Message, state: FSMContext):
    data = await state.get_data()
    district = data["district"]
    farm = data["farm"]
    try:
        db.add_farmer(name=message.text, farm=farm)
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

    if os.path.exists(f"download\excel\{district_name}"): path_district_excel = f"download\excel\{district_name}"  
    if os.path.exists(f"download\word\{district_name}"): path_district_word = f"download\word\{district_name}"  
    else: 
        os.mkdir(f"download\excel\{district_name}")
        path_district_excel = f"download\excel\{district_name}"

        os.mkdir(f"download\word\{district_name}")
        path_district_word = f"download\word\{district_name}"

    mode = 0o666
    path_excel = os.path.join(str(path_district_excel), farm_name)
    path_word = os.path.join(str(path_district_word), farm_name)
    if os.path.exists(path_excel):
        return
    else:
        os.mkdir(path_excel, mode)

    if os.path.exists(path_word):
        return
    else:
        os.mkdir(path_word, mode)

@dp.callback_query_handler(AdminFilter(), farmer_callback.filter(item_name="del_item"))
async def del_farmer(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    district_id = callback_data.get("item_id")
    farm_id = callback_data.get("_item_id")
    await call.message.edit_reply_markup()
    markup = await farmer_keyboards(district_id=district_id, farm_id=farm_id, delete=True)
    await call.message.answer("Бўлим танланг", reply_markup=markup)
    await state.update_data(farm_id=farm_id, district_id=district_id)
    await state.set_state("del_farmer")


@dp.callback_query_handler(AdminFilter(), menu_cd.filter(), state="del_farmer")
async def delete_farmer_request(call: types.CallbackQuery, callback_data: dict, state:FSMContext):
    markup = await yes_no_keyboards()
    farmer_id = callback_data.get("farmer")
    await state.update_data(farmer_id=farmer_id)
    await call.message.edit_text("Rostan o'chirasizmi ?")
    await call.message.edit_reply_markup(markup)
    await state.set_state("confirm_farmer")


@dp.callback_query_handler(AdminFilter(), state="confirm_farmer", text="no_keyboard")
async def del_district_from_db_cancel(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text('Бўлим танланг')
    data = await state.get_data()
    district = data.get("district_id")
    farm = data.get("farm_id")
    await list_farmers(call, district, farm)
    await state.finish()


@dp.callback_query_handler(AdminFilter(), state="confirm_farmer", text="yes_keyboard")
async def del_farmer_from_db(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    farm_id = data["farm_id"]
    district_id = data["district_id"]
    farmer_id = data.get("farmer_id")

    try:
        farmer = db.get_farmer_one(farmer_id=farmer_id)[0][1]
        
        farmer_info = db.get_farmer_info(farmer_id=farmer_id)
        district_name = farmer_info[0][3]
        farm_name = farmer_info[0][2]
        file_name = farmer_info[0][5]
        file_name_map = farmer_info[0][6]
        file_path = f"download\excel\{district_name}\{farm_name}\{file_name}"
        file_path_map = f"download\word\{district_name}\{farm_name}\{file_name_map}"
        
        if os.path.exists(file_path):
            os.remove(file_path)
            print("File deleted successfully.")
        if os.path.exists(file_path_map):
            os.remove(file_path_map)
            print("File deleted successfully.")
        else:
            print("File not found.")

        db.delete_farmer(id=farmer_id)
        await call.answer(f"✅ {farmer} ўчирилди", cache_time=1)
        
        await call.message.edit_text("Бўлим танланг")
        await list_farmers(callback=call, district=district_id, farm=farm_id)
    except Exception as err:
        print("Farmer o'chirishda xatolik", err)
    finally:
        await state.finish()






@dp.callback_query_handler(AdminFilter(), menu_cd.filter(), state="*")
async def cancel_one_farmer(call: CallbackQuery, callback_data: dict, state: FSMContext):
    cancel = callback_data.get("cancel")
    district_id = callback_data.get("district")
    farm_id = callback_data.get("farm")
    farmer_id = callback_data.get("farmer")

    if cancel == "farm_cancel":
        await list_farms(callback=call, district=district_id)
    if cancel == "farmer_cancel":
        await list_farmers(callback=call, district=district_id, farm=farm_id)
    if cancel == "one_farmer_cancel":
        await list_farmers(call, district_id, farm_id)
    if cancel == "update_files_cancel":
        await show_item(call, district_id, farm_id, farmer_id)
    else:
        await state.finish()