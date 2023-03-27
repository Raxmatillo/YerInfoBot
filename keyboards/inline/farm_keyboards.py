from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData

from loader import db

menu_cd = CallbackData("menu", "level", "district", "farm", "farmer")
excel_cd = CallbackData("excel", "farmer_id")
def make_callback_data(level, district="0", farm="0", farmer="0"):
    return menu_cd.new(
        level=level, district=district, farm=farm, farmer=farmer
    )


async def district_keyboards():
    CURRENT_LEVEL = 0

    markup = InlineKeyboardMarkup(row_width=2)

    districts = db.get_district()
    for district in districts:
        button_text = f"{district[1]} туман"
        callback_data = make_callback_data(
            level=CURRENT_LEVEL+1, district=district[0]
        )
        markup.insert(
            InlineKeyboardButton(text=button_text, callback_data=callback_data)
        )

    return markup

async def farm_keyboards(district_id: int):
    CURRENT_LEVEL = 1
    markup = InlineKeyboardMarkup(row_width=2)
    farms = db.get_farm(district_id=district_id)
    for farm in farms:
        button_text = f"{farm[1]}"
        callback_data = make_callback_data(
            level=CURRENT_LEVEL+1,
            district=district_id,
            farm=farm[0]
        )
        markup.insert(
            InlineKeyboardButton(text=button_text, callback_data=callback_data)
        )
    markup.row(
        InlineKeyboardButton(
            text="⬅️Ortga",
            callback_data=make_callback_data(level=CURRENT_LEVEL-1)
        )
    )
    return markup

async def farmer_keyboards(district_id: int, farm_id: int):
    CURRENT_LEVEL = 2
    markup = InlineKeyboardMarkup(row_width=2)
    farmers = db.get_farmer(farm_id=farm_id)
    for farm in farmers:
        button_text = f"{farm[1]}"
        callback_data = make_callback_data(
            level=CURRENT_LEVEL+1,
            district=district_id,
            farm=farm_id,
            farmer=farm[0]
        )
        markup.insert(
            InlineKeyboardButton(text=button_text, callback_data=callback_data)
        )
    markup.row(
        InlineKeyboardButton(
            text="⬅️Ortga",
            callback_data=make_callback_data(
                level=CURRENT_LEVEL-1, district=district_id
            )
        )
    )
    return markup


async def one_farmer_keyboards(district_id: int, farm_id: int, farmer_id:
int, admin: bool=False):
    CURRENT_LEVEL = 3
    markup = InlineKeyboardMarkup(row_width=1)
    markup.insert(
        InlineKeyboardButton(
            text="⬅️Ortga",
            callback_data=make_callback_data(
                level=CURRENT_LEVEL-1, district=district_id, farm=farm_id,
                farmer=farmer_id
            )
        )
    )
    if admin:
        markup.row(
            InlineKeyboardButton(
                text="Yangilash",
                callback_data=excel_cd.new(farmer_id=farmer_id)
            )
        )
    return markup