# bot.py

import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Telegram Token
API_TOKEN = "7993407575:AAFa8RG9wOrLjnDXfTOJfhsu60tXHZNENr4"

# Настройка Google Sheets
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
CREDS = ServiceAccountCredentials.from_json_keyfile_name("instant-avatar-456707-q7-0d3a1711d3e1.json", SCOPE)
client = gspread.authorize(CREDS)
sheet = client.open("azv").sheet1  # Имя таблицы

# FSM состояние
class Register(StatesGroup):
    name = State()
    age = State()

# Создаем бота
bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Команда /start
@dp.message(Command("start"))
async def start_handler(message: types.Message, state: FSMContext):
    await message.answer("Привет! Как тебя зовут?")
    await state.set_state(Register.name)

@dp.message(Register.name)
async def get_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Сколько тебе лет?")
    await state.set_state(Register.age)

@dp.message(Register.age)
async def get_age(message: types.Message, state: FSMContext):
    user_data = await state.update_data(age=message.text)
    await state.clear()

    # Сохраняем в Google Sheets
    sheet.append_row([
        str(message.from_user.id),
        user_data['name'],
        user_data['age'],
        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ])

    await message.answer("Спасибо! Ты зарегистрирован ✅")

# Запуск
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    print("Бот запущен")
