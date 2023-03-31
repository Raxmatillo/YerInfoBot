import os

from aiogram import types
from aiogram.dispatcher import FSMContext

from keyboards.default.menu import empty_keyboard
from keyboards.inline.farm_keyboards import excel_cd
from loader import dp, db

from states.FarmerState import AddFarmer, UpdateExcel




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
    await call.message.edit_reply_markup()
    farmer_id = callback_data.get("farmer_id")
    farm_id = callback_data.get("farm_id")
    district_id = callback_data.get("district_id")
    await state.update_data({"district_id":district_id,
                             "farm_id":farm_id,
                             "farmer_id":farmer_id})
    await call.message.answer("Хўжаликнинг <b>excel(.xlsx/.xls)</b> файлини "
                              "юборинг...", parse_mode='HTML')

    await UpdateExcel.get_excel.set()

@dp.message_handler(state=UpdateExcel.get_excel, content_types="document")
async def get_excel_file(message: types.Message, state: FSMContext):
    doc_id = message.document.file_id
    data = await state.get_data()
    district_id = data.get("district_id")
    farm_id = data.get("farm_id")
    farmer_id = data.get("farmer_id")


    try:
        excels = sorted([x for x in os.listdir('download')])
        for excel in excels:
            if excel.startswith(f"{district_id}-{farm_id}"
                                f"-{farmer_id}"):
                os.remove(f"download/{excel}")
        await message.document.download(
            destination_file=f"download/{district_id}-{farm_id}-{farmer_id}"
                             f"-{message.document.file_name}")

        db.update_excel(excel=doc_id, id=farmer_id)
        await message.answer("Muvaffaqiyatli yangilandi!")
        await state.finish()
    except Exception as err:
        print(err)
