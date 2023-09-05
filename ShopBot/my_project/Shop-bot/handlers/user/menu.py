
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup
from loader import dp
from filters import IsAdmin, IsUser

catalog = '🛍️ Каталог'
cart = '🛒 Корзина'
info = 'ℹ️ Инфо'
ask_question = '❓ Задать вопрос'
back_button = '🔙 Назад'

settings = '⚙️ Настройка каталога'
orders = '🚚 Заказы'
questions = '❓ Вопросы'


def generate_main_menu_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add(catalog)
    markup.add(cart)
    markup.add(info)
    markup.add(ask_question)
    return markup


@dp.message_handler(IsAdmin(), commands='menu')
async def admin_menu(message: Message):
    markup = ReplyKeyboardMarkup(selective=True)
    markup.add(settings)
    markup.add(questions, orders)
    await message.answer('Меню', reply_markup=markup)


@dp.message_handler(IsUser(), commands='menu')
async def user_menu(message: Message):
    markup = generate_main_menu_markup()
    await message.answer('Меню', reply_markup=markup)


@dp.message_handler(IsUser(), text=info)
async def cmd_info(message: Message):
    await message.answer(
        '<b>О нас:</b>\nРады предложить вам удобный и простой способ покупки качественной одежды и обуви от ведущих мировых брендов.',
        parse_mode='HTML')
        '<b>Помощь и сотрудничество:</b>\nОстались вопросы? Нужна помощь с доставкой оптовых партий из Китая? От карандашей до модульных домов. Брендирование, переговоры, упаковка, проверка, карго. Пишите мне —',
        parse_mode='HTML')


@dp.message_handler(IsUser(), text='назад')
async def cmd_back(message: Message):
    markup = generate_main_menu_markup()
    await message.answer('Меню', reply_markup=markup)
