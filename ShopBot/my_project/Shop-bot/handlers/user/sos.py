from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove
from keyboards.default.markups import all_right_message, cancel_message, submit_markup
from aiogram.types import Message
from states import SosState
from filters import IsUser
from loader import dp, db
from handlers.user.menu import ask_question, generate_main_menu_markup

back_button = "Назад"


@dp.message_handler(IsUser(), text=ask_question)
async def cmd_sos(message: Message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add(back_button)
    await SosState.question.set()
    await message.answer('В чем суть проблемы? Опишите как можно детальнее и администратор обязательно вам ответит.', reply_markup=markup)


@dp.message_handler(IsUser(), text=back_button, state=SosState.question)
async def process_back_button(message: Message, state: FSMContext):
    await state.finish()
    markup = generate_main_menu_markup()
    await message.answer('Вы вернулись в главное меню', reply_markup=markup)


@dp.message_handler(state=SosState.question)
async def process_question(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['question'] = message.text

    await message.answer('Убедитесь, что все верно.', reply_markup=submit_markup())
    await SosState.next()


@dp.message_handler(lambda message: message.text not in [cancel_message, all_right_message], state=SosState.submit)
async def process_price_invalid(message: Message):
    await message.answer('Такого варианта не было.')


@dp.message_handler(text=cancel_message, state=SosState.submit)
async def process_cancel(message: Message, state: FSMContext):
    await message.answer('Отменено!', reply_markup=ReplyKeyboardRemove())
    await state.finish()
    markup = generate_main_menu_markup()
    await message.answer('Вы вернулись в главное меню', reply_markup=markup)


@dp.message_handler(text=all_right_message, state=SosState.submit)
async def process_submit(message: Message, state: FSMContext):

    cid = message.chat.id

    if db.fetchone('SELECT * FROM questions WHERE cid=?', (cid,)) == None:

        async with state.proxy() as data:
            db.query('INSERT INTO questions VALUES (?, ?)',
                     (cid, data['question']))

        await message.answer('Отправлено!', reply_markup=ReplyKeyboardRemove())

    else:

        await message.answer('Превышен лимит на количество задаваемых вопросов.', reply_markup=ReplyKeyboardRemove())

    await state.finish()
    markup = generate_main_menu_markup()
    await message.answer('Вы вернулись в главное меню', reply_markup=markup)
