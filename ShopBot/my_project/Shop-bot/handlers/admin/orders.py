from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from loader import dp, db
from handlers.user.menu import orders
from filters import IsAdmin
import json
import sqlite3


@dp.message_handler(IsAdmin(), text=orders)
async def process_orders(message: Message):
    try:
        orders = db.fetchall('SELECT * FROM orders WHERE status IS NULL OR status != ?', ('Обработано',))
        if len(orders) == 0:
            await message.answer('У вас нет заказов.')
        else:
            for order in orders:
                await order_answer(message, order)
    except Exception as e:
        await message.answer(f'Произошла ошибка при обработке заказов: {e}')


async def order_answer(message, order):
    res = f'Заказ <b>{order[0]}</b>\n\n'
    res += f'Имя: {order[1]}\n'  # имя пользователя
    res += f'Адрес: {order[2]}\n'  # адрес пользователя
    try:
        # Преобразование строки продуктов в словарь
        products_dict = dict(item.split("=") for item in order[3].split())
        # Извлечение информации о каждом продукте
        for product_id, quantity in products_dict.items():
            product_info = db.fetchone('SELECT * FROM products WHERE idx = ?', (product_id,))
            if product_info:
                res += f'Продукт: {product_info[1]} (id: {product_id}), Количество: {quantity}\n'
        # Добавляем кнопку обработки
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("Обработать", callback_data=f"process_{order[0]}"))
        await message.answer(res, reply_markup=markup)
    except Exception as e:
        res += f'Произошла ошибка при обработке информации о продуктах в заказе: {e}\n'
        await message.answer(res)


@dp.callback_query_handler(lambda c: c.data.startswith('process_'))
async def process_order(callback_query: CallbackQuery):
    order_id = callback_query.data.split("_")[1]
    try:
        conn = sqlite3.connect('./data/database.db')
        cursor = conn.cursor()
        cursor.execute('UPDATE orders SET status = ? WHERE cid = ?', ('Обработано', order_id))
        conn.commit()
        await callback_query.message.edit_text('Заказ обработан')
    except Exception as e:
        await callback_query.message.edit_text(f'Произошла ошибка при обработке заказа: {e}')
