from aiogram.dispatcher.filters.state import State, StatesGroup

class YesOrNoState(StatesGroup):
    confirm = State()