from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup)

rp_button = [
    [KeyboardButton(text="Zayafka qo'shish"),
     KeyboardButton(text="Zayafka ko'rish"),
     KeyboardButton(text="Guruhga habar jo'natish")
     ],
]

main_rp = ReplyKeyboardMarkup(keyboard=rp_button, resize_keyboard=True)


def order_keyboard():
    ikm = InlineKeyboardMarkup()
    ikm.add(InlineKeyboardButton('Оставить заявку', callback_data='order_start'))
    return ikm


def food_delete():
    ikm = InlineKeyboardMarkup()
    ikm.add(InlineKeyboardButton("delete", callback_data='delete'))
    return ikm


def order_keyboart():
    ikm = InlineKeyboardMarkup()
    ikm.add(InlineKeyboardButton("o'chirish", callback_data="o'chirish"))
    return ikm
