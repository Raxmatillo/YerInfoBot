import os

from aiogram import types
from aiogram.dispatcher import FSMContext
from keyboards.inline.farm_keyboards import farmer_keyboards
from data.config import ADMINS
from keyboards.default.menu import cancel_keyboard, menu
from keyboards.inline.farm_keyboards import excel_cd, update_file_keyboards
from loader import dp, db

from filters import AdminFilter

from utils.misc.my_functions import excel

from states.FarmerState import UpdateExcel


@dp.message_handler(AdminFilter(), text="Бекор қилиш", state="*")
async def cancel_handler(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Амал бекор қилинди", reply_markup=menu)


# @dp.message_handler(commands="add_farmer")
# async def add_farmer_start(message: types.Message):
#     await message.answer("Menga fermerni yuboring")
#     await AddFarmer.name.set()

# @dp.message_handler(state=AddFarmer.name)
# async def get_farmer_name(message: types.Message, state: FSMContext):
#     await state.update_data({"name":message.text})
#     await message.answer("Excel файл бўса юборинг ёки **⚪️Бўш қолдириш** "
#                          "тугмасини босинг",
#                          reply_markup=empty_keyboard)
#     await AddFarmer.excel.set()

# @dp.message_handler(state=AddFarmer.excel)
# async def get_farmer_excel(message: types.Message, state: FSMContext):
#     await state.update_data({"excel":message.document.file_id})


# @dp.callback_query_handler(excel_cd.filter())
# async def send_file_handler(call: types.CallbackQuery, callback_data: dict):
#     await call.message.edit_reply_markup()
#     farmer_id = callback_data.get("farmer_id")
#     farm_id = callback_data.get("farm_id")
#     district_id = callback_data.get("district_id")
#     type = callback_data.get("type")
#     item = db.get_farmer_one(farmer_id=farmer_id)
#     if type == "excel":
#         if item[0][-2] == None:
#             await call.message.edit_text("Fayl mavjud emas")
#         else:
#             if call.from_user.id == int(ADMINS[0]):
#                 markup = await back_keyboard(district_id=district_id,
#                                                     farm_id=farm_id,
#                                                     farmer_id=farmer_id,
#                                                     admin=True)
#             else:
#                 markup = await back_keyboard(district_id=district_id,
#                                              farm_id=farm_id,
#                                              farmer_id=farmer_id,
#                                              admin=False)
#
#             await call.message.answer_document(document=item[0][-2],
#                                                reply_markup=ma)

@dp.callback_query_handler(excel_cd.filter()) # text_contains="🔄 Янгилаш"
async def update_file(call: types.CallbackQuery, callback_data: dict,
                      state: FSMContext):
    await call.message.edit_reply_markup()
    farmer_id = callback_data.get("farmer_id")
    farm_id = callback_data.get("farm_id")

    # farmer_info = db.get_farmer_info(farmer_id=farmer_id)
    
    # district_name = farmer_info[0][1]
    # farm_name = farmer_info[0][2]
    # path_district = f"download/excel/{district_name}" if os.path.exists(path=f"download/excel/{district_name}") else os.mkdir(f"download/excel/{district_name}")
    # path_farm = f"{path_district}/{farm_name}" if os.path.exists(path=f"{path_district}/{district_name}") else os.mkdir(f"{path_district}/{farm_name}")

    district_id = callback_data.get("district_id")
    await state.update_data({"district_id":district_id,
                             "farm_id":farm_id,
                             "farmer_id":farmer_id
                             }
                            )   
    markup = await update_file_keyboards(district_id, farm_id, farmer_id)
    await call.message.answer("Янгиламоқчи бўлган файлни танланг",
                              parse_mode='HTML', reply_markup=markup)
    await UpdateExcel.select_file.set()

# @dp.callback_query_handler(menu_cd.filter(), state=UpdateExcel.select_file)
# async def cancel_update_file_handler(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
#     cancel = callback_data.get("cancel")
#     district_id = callback_data.get("district")
#     farmer_id = callback_data.get("farmer")
#     farm_id = callback_data.get("farm")
#     if cancel == "update_files_cancel":
#         await show_item(call, district_id, farm_id, farmer_id)
        
@dp.callback_query_handler(excel_cd.filter(), state=UpdateExcel.select_file)
async def update_excel(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    await call.message.edit_reply_markup()
    type = callback_data.get("type")
    if type == "excel":
        await state.update_data({'type': 'excel'})
    elif type == "word":
        await state.update_data({'type': 'word'})
    else:
        await state.update_data({'type': 'None'})
    await call.message.answer("Файлни юборинг", reply_markup=cancel_keyboard)
    await UpdateExcel.get_excel.set()

@dp.message_handler(state=UpdateExcel.get_excel, content_types="document")
async def get_excel_file(message: types.Message, state: FSMContext):
    doc_id = message.document.file_id
    async with state.proxy() as data:
        district_id = data.get("district_id")
        farm_id = data.get("farm_id")
        farmer_id = data.get("farmer_id")
        type = data.get("type")

    farmer_info = db.get_farmer_info(farmer_id=farmer_id)
    district_name = farmer_info[0][3]
    farm_name = farmer_info[0][2]
    file_name = farmer_info[0][5]
    file_name_map = farmer_info[0][6]

    if type == "excel":
        try:
            path = f'download\excel\{district_name}\{farm_name}\\'
            file = f"{path}\{message.document.file_name}"
            xabar = await message.answer("Текширилмоқда...")

            await message.document.download(
                destination_file=file)
            try:
                _file = excel(excel_file=file)
            except Exception as err:
                print(err)
                await message.answer("Файл мос эмас, файлни текширинг ва қайта юборинг !")
                return
            
            file_path = f"download\excel\{district_name}\{farm_name}\{file_name}"
            if os.path.exists(file_path):
                os.remove(file_path)
                print("File deleted successfully.")
            else:
                print("File not found!")

            db.update_excel(excel=doc_id, file_name=message.document.file_name, id=farmer_id)
            markup = await farmer_keyboards(district_id, farm_id)
            await xabar.delete()
            await message.answer("Юкланди", reply_markup=types.ReplyKeyboardRemove())
            await message.answer("Муваффақиятли янгиланди!", reply_markup=markup)
            await state.finish()
        except Exception as err:
            print(err)
    elif type == "word":
        path = f'download\word\{district_name}\{farm_name}\\'
        file = f"{path}\{message.document.file_name}"
        try:
            xabar = await message.answer("Юкланмоқда...")

            await message.document.download(
                destination_file=file)
            
            file_path_map = f"download\word\{district_name}\{farm_name}\{file_name_map}"
            if os.path.exists(file_path_map):
                os.remove(file_path_map)
                print("File deleted successfully.")
            else:
                print("File not found.")
                
            db.update_word(word=doc_id, file_name_map=message.document.file_name, id=farmer_id)
            markup = await farmer_keyboards(district_id, farm_id)
            await xabar.delete()
            await message.answer("Юкланди", reply_markup=types.ReplyKeyboardRemove())
            await message.answer("Муваффақиятли янгиланди!", reply_markup=markup)
            await state.finish()
        except Exception as err:
            print(err)


@dp.message_handler(state=UpdateExcel.get_excel, content_types="document")
async def unknown_update_file(message: types.Message):
    await message.answer('Файлни юборинг')