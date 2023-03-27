from aiogram import types
from aiogram.dispatcher import FSMContext

from keyboards.default.menu import empty_keyboard
from keyboards.inline.farm_keyboards import excel_cd
from loader import dp, db

from pathlib import Path

from states.FarmerState import AddFarmer, UpdateExcel

download_path = Path().joinpath("downloads")
download_path.mkdir(parents=True, exist_ok=True)




@dp.message_handler(commands="add_farmer")
async def add_farmer_start(message: types.Message):
    await message.answer("Menga fermerni yuboring")
    await AddFarmer.name.set()

@dp.message_handler(state=AddFarmer.name)
async def get_farmer_name(message: types.Message, state: FSMContext):
    await state.update_data({"name":message.text})
    await message.answer("Excel файл бўса юборинг ёки **⚪️Бўш қолдириш** "
                         "тугмасини босинг",
                         reply_markup=empty_keyboard)
    await AddFarmer.excel.set()

@dp.message_handler(state=AddFarmer.excel)
async def get_farmer_excel(message: types.Message, state: FSMContext):
    await state.update_data({"excel":message.document.file_id})

@dp.callback_query_handler(excel_cd.filter(), state=UpdateExcel.go_state)
async def update_file(call: types.CallbackQuery, callback_data: dict,
                      state: FSMContext):
    farmer_id = callback_data.get("farmer_id")
    await state.update_data({"farmer_id":farmer_id})
    await call.message.answer("Хўжаликнинг <b>excel(.xlsx/.xls)</b> файлини "
                              "юборинг...", parse_mode='HTML')

    await UpdateExcel.get_excel.set()

@dp.messaage_handler(state=UpdateExcel.get_excel, content_types="document")
async def get_excel_file(message: types.Message, state: FSMContext):
    await message.document.download(destination=download_path)
    doc_id = message.document.file_id
    data = await state.get_data()
    farmer_id = data.get("farmer_id")
    try:
        db.update_excel(excel=doc_id, id=farmer_id)
        await message.answer("Muvaffaqiyatli yangilandi!")
    except Exception as err:
        print(err)
