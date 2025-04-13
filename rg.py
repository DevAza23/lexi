import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

# === Безопасность: берем токен из переменной окружения ===
API_TOKEN = os.getenv("BOT_TOKEN")

# === Google Sheets Auth ===
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Загружаем credentials.json (должен быть в корне проекта)
CREDS = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", SCOPE)
client = gspread.authorize(CREDS)
sheet = client.open("azv").sheet1  # Имя таблицы

# === FSM состояния ===
class Register(StatesGroup):
    name = State()
    age = State()

# === Создаем бота и диспетчер ===
bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# === Обработчики ===
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

    # Сохраняем в таблицу
    sheet.append_row([
        str(message.from_user.id),
        user_data["name"],
        user_data["age"],
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ])

    await message.answer("Спасибо! Ты зарегистрирован ✅")

# === Запуск ===
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
