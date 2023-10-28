from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types
def get_keyboard():
    buttons = [
        [
            types.InlineKeyboardButton(text="Подтвердить", callback_data="add_name_bd")
        ],
        [
            types.InlineKeyboardButton(text="Изменить", callback_data="reply_step_one"),
        ]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

def get_keyboard_admin():
    buttons = [
        [
            types.InlineKeyboardButton(text="Рассылка на доставки", callback_data="spam")
        ],
        [
            types.InlineKeyboardButton(text="Выгрузить файл на доставку", callback_data="get_file_dostavka"),
        ],
        [
            types.InlineKeyboardButton(text="Сбор товара", callback_data="get_cart_user"),
        ],
        [
            types.InlineKeyboardButton(text="Подтвердить выполненные доставки", callback_data="check_dostavki"),
        ]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

def get_keyboard_back_work():
    buttons = [
        types.InlineKeyboardButton(text="Назад", callback_data="back_work")
    ],
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

def get_keyboard_clear():
    buttons = [
        types.InlineKeyboardButton(text="Очистить корзину", callback_data="clear_cart")
    ],
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard
