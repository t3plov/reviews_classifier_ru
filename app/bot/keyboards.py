from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

main_menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='✉️ Анализ отдельного отзыва')],
        [KeyboardButton(text='🗂 Анализ пакета отзывов')],
        [KeyboardButton(text='ℹ️ О боте'),
         KeyboardButton(text='🆘 Помощь')]
    ],
    resize_keyboard=True
)

def back_to_menu():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='⏪ Вернуться в меню', callback_data='back_to_menu')]
        ]
    )
    return keyboard
