from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData

class ViewProduct(CallbackData, prefix="id_product"):
    action: str
    id: int
    msg_id: int
def view_product(caption: list, id: list, msg_id: list):
    builder = InlineKeyboardBuilder()
    for i in range(len(caption)):
        builder.row(
            InlineKeyboardButton(text=caption[i], inline_keyboard_markup=3, callback_data=ViewProduct(action="refusal[{i}]".format(i=i), id=id[i], msg_id=msg_id[i]).pack()),

        )
    return builder.as_markup()