import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext
import asyncio
from config_14_4 import *
from crud_functions import *


logging.basicConfig(level=logging.INFO)

initiate_db()  #  создание и наполнение БД в файле crud_functions

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

kb = ReplyKeyboardMarkup(resize_keyboard=True)
buttons = ['Рассчитать', 'Информация']
kb.add(*buttons)

button_buy = 'Купить'
kb.add(button_buy)

kb_inline = types.InlineKeyboardMarkup(row_width=1)
button_calc_inline = types.InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='calories')
button_info_inline = types.InlineKeyboardButton(text='Узнать формулу расчета для мужчин',
                                          callback_data='formulas')

kb_inline.add(button_calc_inline, button_info_inline)

menu_buying_inline = types.InlineKeyboardMarkup(row_width=N)
for i in range(1, N + 1):
    buying_inline_button = InlineKeyboardButton(text=f'Продукт {i}', callback_data='product_buying')
    menu_buying_inline.insert(buying_inline_button)

class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()

@dp.message_handler(text=['Рассчитать'])
async def main_menu(message):
    await message.answer('Выберите опцию:', reply_markup=kb_inline)

@dp.callback_query_handler(text='formulas')
async def get_formulas(call):
    await call.message.answer('10 х вес (кг) + 6,25 x рост (см) – 5 х возраст (г) + 5')
    await call.answer()

@dp.message_handler(commands=['start'])
async def starter(message):
    await message.answer('Привет! Я бот, помогающий Вашему здоровью!', reply_markup=kb)
    await message.answer('Нажмите кнопку "Рассчитать", чтобы узнать суточную норму Ваших калорий\n'
                         'Нажмите кнопку "Информация", чтобы узнать используемый метод расчета нормы калорий\n'
                         'Нажмите кнопку "Купить", чтобы выбрать продукт')

@dp.message_handler(text=['Информация'])
async def inform(message):
    await message.answer('Использован упрощенный вариант формулы Миффлина - Сан Жеора для мужчин')

@dp.callback_query_handler(text=['calories'])
async def set_age(call):
    await call.message.answer('Введите свой возраст:')
    await UserState.age.set()

@dp.message_handler(state=UserState.age)
async def set_growth(message, state):
    await state.update_data(age=message.text)
    await message.answer('Введите свой рост (см):')
    await UserState.growth.set()

@dp.message_handler(state=UserState.growth)
async def set_weight(message, state):
    await state.update_data(growth=message.text)
    await message.answer('Введите свой вес (кг):')
    await UserState.weight.set()

@dp.message_handler(state=UserState.weight)
async def send_calories(message, state):
    await state.update_data(weight=message.text)
    await UserState.weight.set()
    data = await state.get_data()
    await message.answer(f"Ваша норма калорий: "
                         f"{10 * float(data['weight']) + 6.25 * float(data['growth']) - 5 * float(data['age']) + 5}")
    await message.answer('Для возврата в основное меню введите команду /start')
    await state.finish()

@dp.message_handler(text=['Купить'])
async def get_buying_list(message):
    for i in range(1, N + 1):
        await message.answer(get_all_products()[i - 1])
        with open(f'images/image{i}.jpg', 'rb') as img:
            await message.answer_photo(img)
    await message.answer('Выберите продукт для покупки:', reply_markup=menu_buying_inline)

@dp.callback_query_handler(text=['product_buying'])
async def send_confirm_message(call):
    await call.message.answer('Вы успешно приобрели продукт!')
    await call.answer()

@dp.message_handler()
async def all_messages(message):
    await message.answer('Введите команду /start, чтобы начать общение')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
