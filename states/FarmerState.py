from aiogram.dispatcher.filters.state import State, StatesGroup


class AddFarmer(StatesGroup):
    name = State()
    excel = State()


class UpdateExcel(StatesGroup):
    go_state = State()
    get_excel = State()