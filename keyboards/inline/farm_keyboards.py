from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData

from loader import db

menu_cd = CallbackData("menu", "level", "district", "farm", "farmer", "delete", "cancel")
excel_cd = CallbackData("excel", "district_id", "farm_id", "farmer_id", "type")
def make_callback_data(level, district="0", farm="0", farmer="0", delete=False, cancel=""):
    return menu_cd.new(
        level=level, district=district, farm=farm, farmer=farmer, delete=delete, cancel=cancel
    )


async def district_keyboards(delete: bool=False):
    CURRENT_LEVEL = 0

    markup = InlineKeyboardMarkup(row_width=2)

    districts = db.get_district()
    for district in districts:
        button_text = f"{'➖ ' if delete else ''} {district[1]}"
        callback_data = make_callback_data(
            level=CURRENT_LEVEL+1, district=district[0], delete=True if delete else False
        )
        markup.insert(
            InlineKeyboardButton(text=button_text, callback_data=callback_data)
        )
        
    return markup

async def farm_keyboards(district_id: int, delete: bool=False):
    CURRENT_LEVEL = 1
    markup = InlineKeyboardMarkup(row_width=2)
    farms = db.get_farm(district_id=district_id)

    for farm in farms:
        button_text = f"{'➖ ' if delete else ''}{farm[1]}"
        callback_data = make_callback_data(
            level=CURRENT_LEVEL+1,
            district=district_id,
            farm=farm[0],
            delete=True if delete else False
        )
        markup.insert(
            InlineKeyboardButton(text=button_text, callback_data=callback_data)
        )

    # if delete==False:
    markup.row(
        InlineKeyboardButton(
            text="⬅️ Ортга",
            callback_data=make_callback_data(level=CURRENT_LEVEL-1, cancel="farm_cancel")
        )
    )
    return markup



async def farmer_keyboards(district_id: int, farm_id: int, delete: bool=False):
    CURRENT_LEVEL = 2
    markup = InlineKeyboardMarkup(row_width=2)
    farmers = db.get_farmer(farm_id=farm_id)
    

    for farm in farmers:
        button_text = f"{'➖ ' if delete else ''}{farm[1]}"
        callback_data = make_callback_data(
            level=CURRENT_LEVEL+1,
            district=district_id,
            farm=farm_id,
            farmer=farm[0],
            delete=True if delete else False,
        )
        markup.insert(
            InlineKeyboardButton(text=button_text, callback_data=callback_data)
        )


    markup.row(
        InlineKeyboardButton(
            text="⬅️ Ортга",
            callback_data=make_callback_data(
                level=CURRENT_LEVEL-1, district=district_id, cancel="farmer_cancel"
            )
        )
    )
    return markup


async def one_farmer_keyboards(
        district_id: int,
        farm_id: int,
        farmer_id: int,
        admin: bool = False):
    CURRENT_LEVEL = 3
    markup = InlineKeyboardMarkup(row_width=2)

    markup.row(
        InlineKeyboardButton(
            text="⬅️ Ортга",
            callback_data=make_callback_data(
                level=CURRENT_LEVEL-1, district=district_id, farm=farm_id,
                farmer=farmer_id
            )
        )
    )
    if admin:
        markup.row(
            InlineKeyboardButton(
                text="🔄 Янгилаш",
                callback_data=excel_cd.new(
                    district_id=district_id,
                    farm_id=farm_id,
                    farmer_id=farmer_id,
                    type="None"
                )
            )
        )
    return markup

async def update_file_keyboards(
        district_id: int,
        farm_id: int,
        farmer_id: int
):
    CURRENT_LEVEL = 3
    markup = InlineKeyboardMarkup(row_width=2)
    markup.insert(
        InlineKeyboardButton(
            text="Excel",
            callback_data=excel_cd.new(
                district_id=district_id,
                farm_id=farm_id,
                farmer_id=farmer_id,
                type="excel"
            )
        )
    )
    markup.insert(
        InlineKeyboardButton(
            text="Word",
            callback_data=excel_cd.new(
                district_id=district_id,
                farm_id=farm_id,
                farmer_id=farmer_id,
                type="word"
            )
        )
    )

    markup.row(
        InlineKeyboardButton(
            text="⬅️ Ортга",
            callback_data=make_callback_data(
                level=CURRENT_LEVEL - 1, district=district_id, farm=farm_id,
                farmer=farmer_id
            )
        )
    )

    return markup