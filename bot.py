import asyncio
import os
import requests
from aiogram import Bot, Dispatcher, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command, StateFilter

# Извлечение токена из переменной окружения и инициализация объекта бота
bot_token = os.getenv("TELEGRAM_BOT_TOKEN")

bot = Bot(token=bot_token)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
router = Router()
dp.include_router(router)

# Определение состояний FSM
class CurrencyStates(StatesGroup):
    manage_action = State()
    currency_name = State()
    currency_rate = State()
    delete_currency = State()
    change_rate = State()
    convert_currency = State()
    convert_amount = State()

# Список администраторов
ADMIN_USERS = [651245921]

# Меню для администратора
admin_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="/add_currency"), KeyboardButton(text="/delete_currency")],
        [KeyboardButton(text="/change_rate"), KeyboardButton(text="/get_currencies")],
        [KeyboardButton(text="/convert")]
    ],
    resize_keyboard=True
)

# Меню для обычных пользователей
user_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="/get_currencies"), KeyboardButton(text="/convert")]
    ],
    resize_keyboard=True
)

# Обработчик команды /start
@router.message(Command("start"))
async def start_command(message: types.Message):
    if message.from_user.id in ADMIN_USERS:
        await message.answer("Привет администратор! Выберите действие:", reply_markup=admin_menu)
    else:
        await message.answer("Привет пользователь! Выберите команду:", reply_markup=user_menu)


# Обработчик команды /manage_currency
@router.message(Command("manage_currency"))
async def manage_currency(message: types.Message, state: FSMContext):
    if message.from_user.id not in ADMIN_USERS:
        await message.answer("У вас нет доступа к этой команде.")
        return
    await message.answer("Выберите действие: добавить, удалить или изменить курс валюты.")
    await state.set_state(CurrencyStates.manage_action)

@router.message(StateFilter(CurrencyStates.manage_action))
async def process_manage_action(message: types.Message, state: FSMContext):
    action = message.text.lower().strip()
    if action == "добавить валюту":
        await message.answer("Введите название новой валюты:")
        await state.set_state(CurrencyStates.currency_name)
    elif action == "удалить валюту":
        await message.answer("Введите название валюты для удаления:")
        await state.set_state(CurrencyStates.delete_currency)
    elif action == "изменить курс валюты":
        await message.answer("Введите название валюты для изменения:")
        await state.set_state(CurrencyStates.change_rate)
    else:
        await message.answer("Неправильное действие. Пожалуйста, выберите добавить, удалить или изменить курс валюты.")
        await state.clear()

@router.message(StateFilter(CurrencyStates.currency_name))
async def add_currency_name(message: types.Message, state: FSMContext):
    currency_name = message.text.strip()
    response = requests.get(f'http://localhost:5001/check_currency_exist?currency_name={currency_name}')
    if response.status_code == 200 and response.json().get('exists'):
        await message.answer("Такая валюта уже существует.")
        await state.clear()
    else:
        await state.update_data(currency_name=currency_name)
        await state.set_state(CurrencyStates.currency_rate)
        await message.answer(f"Введите курс валюты {currency_name} к рублю:")

@router.message(Command("currency_rate"))
async def add_currency_rate(message: types.Message, state: FSMContext):
    try:
        currency_rate = float(message.text.strip())
        data = await state.get_data()
        currency_name = data['currency_name']
        response = requests.post('http://localhost:5001/load', json={'currency_name': currency_name, 'rate': currency_rate})
        if response.status_code == 200:
            await message.answer(f"Валюта {currency_name} успешно добавлена с курсом {currency_rate} к рублю.")
        else:
            await message.answer("Ошибка при добавлении валюты.")
        await state.clear()
    except ValueError:
        await message.answer("Некорректный формат курса. Введите число.")

@router.message(Command("delete_currency"))
async def delete_currency_command(message: types.Message, state: FSMContext):
    if message.from_user.id not in ADMIN_USERS:
        await message.answer("У вас нет доступа к этой команде.")
        return
    await message.answer("Введите название валюты:")
    await state.set_state(CurrencyStates.delete_currency)

@router.message(StateFilter(CurrencyStates.delete_currency))
async def delete_currency_name(message: types.Message, state: FSMContext):
    currency_name = message.text.strip()
    response = requests.post('http://localhost:5001/delete', json={'currency_name': currency_name})
    if response.status_code == 200:
        await message.answer(f"Валюта {currency_name} успешно удалена.")
    else:
        await message.answer("Ошибка при удалении валюты.")
    await state.clear()

@router.message(StateFilter(CurrencyStates.change_rate))
async def change_currency_rate_name(message: types.Message, state: FSMContext):
    currency_name = message.text.strip()
    response = requests.get(f'http://localhost:5001/check_currency_exist?currency_name={currency_name}')
    if response.status_code == 200 and response.json().get('exists'):
        await state.update_data(currency_name=currency_name)
        await state.set_state(CurrencyStates.currency_rate)
        await message.answer(f"Введите новый курс валюты {currency_name} к рублю:")
    else:
        await message.answer("Такая валюта не найдена.")
        await state.clear()

@router.message(StateFilter(CurrencyStates.currency_name))
async def currency_name(message: types.Message):
    response = requests.get('http://localhost:5002/currencies')
    if response.status_code == 200:
        currencies = response.json()
        if currencies:
            for currency in currencies:
                await message.answer(f"Валюта: {currency['currency_name']} Курс: {currency['rate']}")
        else:
            await message.answer('Список пуст')
    else:
        await message.answer('Ошибка при получении списка валют')

@router.message(Command("convert"))
async def convert_currency(message: types.Message, state: FSMContext):
    await message.answer("Введите название валюты:")
    await state.set_state(CurrencyStates.convert_currency)

@router.message(Command("get_currencies"))
async def get_currencies_command(message: types.Message):
    response = requests.get('http://localhost:5002/currencies')
    if response.status_code == 200:
        currencies = response.json()
        if currencies:
            for currency in currencies:
                await message.answer(f"Валюта: {currency['currency_name']} Курс: {currency['rate']}")
        else:
            await message.answer('Список пуст')
    else:
        await message.answer('Ошибка при получении списка валют')


@router.message(StateFilter(CurrencyStates.convert_currency))
async def convert_currency_name(message: types.Message, state: FSMContext):
    currency_name = message.text.strip()
    await state.update_data(currency_name=currency_name)
    await message.answer("Введите сумму для конвертации:")
    await state.set_state(CurrencyStates.convert_amount)

@router.message(StateFilter(CurrencyStates.convert_amount))
async def convert_currency_amount(message: types.Message, state: FSMContext):
    try:
        amount = float(message.text.strip())
        data = await state.get_data()
        currency_name = data['currency_name']
        response = requests.get(f'http://localhost:5002/convert?currency_name={currency_name}&amount={amount}')
        if response.status_code == 200:
            converted_amount = response.json()['converted_amount']
            await message.answer(f"{amount} {currency_name} = {converted_amount} RUB")
        else:
            await message.answer("Не удалось конвертировать валюту.")
        await state.clear()
    except ValueError:
        await message.answer("Некорректный формат суммы. Введите число.")


# Обработчик команды /add_currency
@router.message(Command("add_currency"))
async def add_currency_command(message: types.Message, state: FSMContext):
    if message.from_user.id not in ADMIN_USERS:
        await message.answer("У вас нет доступа к этой команде.")
        return
    await message.answer("Введите название новой валюты:")
    await state.set_state(CurrencyStates.currency_name)

# Обработчик команды /delete_currency
@router.message(Command("delete_currency"))
async def delete_currency_command(message: types.Message, state: FSMContext):
    if message.from_user.id not in ADMIN_USERS:
        await message.answer("У вас нет доступа к этой команде.")
        return
    await message.answer("Введите название валюты для удаления:")
    await state.set_state(CurrencyStates.delete_currency)

# Обработчик команды /change_rate
@router.message(Command("change_rate"))
async def change_rate_command(message: types.Message, state: FSMContext):
    if message.from_user.id not in ADMIN_USERS:
        await message.answer("У вас нет доступа к этой команде.")
        return
    await message.answer("Введите название валюты для изменения курса:")
    await state.set_state(CurrencyStates.change_rate)

async def main():
    # Запуск бота
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())