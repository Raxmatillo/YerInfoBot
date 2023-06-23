from aiogram.utils.callback_data import CallbackData

district_callback = CallbackData("district", "item_name")
farm_callback = CallbackData("farm", "item_name", "item_id")
farmer_callback = CallbackData("farmer", "item_name", "item_id", "_item_id")