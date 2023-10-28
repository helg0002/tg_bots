from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types.web_app_info import WebAppInfo

def get_keyboard_main():
    buttons = [
        [types.InlineKeyboardButton(text="Основные правила канала", callback_data="get_rules")],
        [
            types.InlineKeyboardButton(text="Корзина", callback_data="view_cart"),

            types.InlineKeyboardButton(text="Задать вопрос", url="https://yandex.ru")

        ],

         [types.InlineKeyboardButton(text="Перейти на канал", url="https://t.me/dsghkfhks")]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

def get_keyboard_back():
    buttons = [
        types.InlineKeyboardButton(text="Назад", callback_data="back")
    ],
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

def get_keyboard_dostavka():
    buttons = [
        types.InlineKeyboardButton(text="Доставка", callback_data="dostavka"),
        types.InlineKeyboardButton(text="Не готов", callback_data="back")
    ],
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

def get_keyboard_buy():
    buttons = [
        types.InlineKeyboardButton(text="Забронировать", callback_data="buy"),
        types.InlineKeyboardButton(text="В бота", url="https://t.me/test_ucenkabot"),

    ],
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

def get_keyboard_address():
    buttons = [
        [
            types.InlineKeyboardButton(text="Подтвердить", callback_data="add_address_bd")
        ],
        [
            types.InlineKeyboardButton(text="Изменить", callback_data="reply_address"),
        ]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def get_keyboard_refusal():
    buttons = [
        types.InlineKeyboardButton(text="Отказ от брони", callback_data="refusal")
    ],
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard