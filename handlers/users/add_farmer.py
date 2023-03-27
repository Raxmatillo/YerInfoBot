from aiogram import types
from aiogram.dispatcher import FSMContext

from loader import dp, db

from pathlib import Path

download_path = Path().joinpath("downloads")
download_path.mkdir(parents=True, exist_ok=True)






from aiogram.dispatcher.filters.state import State, StatesGroup


class AddFarmer(StatesGroup):
    name = State()
    excel = State()


from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

empty_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="⚪️Bo'sh qoldirish")
        ],
    ], row_width=True
)

@dp.message_handler(commands="add_farmer")
async def add_farmer_start(message: types.Message):
    await message.answer("Menga fermerni yuboring")
    await AddFarmer.name.set()

@dp.message_handler(state=AddFarmer.name)
async def get_farmer_name(message: types.Message, state: FSMContext):
    await state.update_data({"name":message.text})
    await message.answer("Excel fayl bo'sa yuboring yoki **⚪️Bo'sh "
                         "qoldirish** tugmasini bosing",
                         reply_markup=empty_keyboard)
    await AddFarmer.excel.set()

@dp.message_handler(state=AddFarmer.excel)
async def get_farmer_excel(message: types.Message, state: FSMContext):
    await state.update_data({"excel":message.document.file_id})




@dp.callback_query_handler(text="update_excel")
async def update_file(call: types.CallbackQuery):
    pass