import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# === Telegram Bot Token ===
API_TOKEN = "993407575:AAFa8RG9wOrLjnDXfTOJfhsu60tXHZNENr4"

# === Google Service Account JSON (замени значения на свои из .json файла) ===
GOOGLE_CREDENTIALS_JSON = {
  "type": "service_account",
  "project_id": "instant-avatar-456707-q7",
  "private_key_id": "0d3a1711d3e1570c1efd670df49ba18865f6f279",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDTALT2Dql0qeeB\nI8mei4GjCTIhwwtnQGrFvgtnb9cSFB5L+0Hl25wdKsUC+sPJVlXw5Z4Ij7WENaGS\n3zhx8jdJir0e1pvQNrrm1vjwpRyhIIl8WDPftC8JZNVIRm5ef7HUaXT4Ve4gnPZO\nT5kkdKkr2cZCbqrhW6TJhQ4dXJLo52tK03L7Hrcst2kipS/lIjpsPQF9dkQKCxHL\nJy3qPNlXHowpgxvJaPJfZ60IVQOITtl+UNHczj0m/BeflC6adb4IAkiV78pWTcxS\nymY2m+nONpoby0k5VK/eVb0GzZowJTZhndkf86BErHKA74UkGJ318aYHj52WJOQM\nToC8zIrrAgMBAAECggEAaTxbBLV/Uo5CxifBMO/HMjct56TNlSuNlR4ZtfcTvxKF\nocOotCl5jRp9s+S5rTsAFeuPjBmQoGXXNdda4Ym6hVVKyYyjnY8OXH8vHWZcBwih\nSYD8LkBBjV/a9/cYqMzrNlN6YTkKUP234orUiFge3533wb5MP6VjZJaV2ZMIOlv5\nNVCKD+Z25Zv7720kBM2BGFWQ7FH/4Z1fQvBYVpNBIsBQyslHzwZ5pUlKRv4PR7tB\nr+pPW9S0fc7ylDb6GtCBWv6Z1Xi2XQ+Jfe4bzYjtRHWCls3pkZpvODGGLJjBAbWD\nuLA/sBi/YYrlzZ5/85rvkcDBcAsroQ4jEJNsbSdMYQKBgQDv+ghfwriAs9k/l3tu\n7c/89ifOx7L4RSBr6lJUsdl66RpNasflgewM6UodDFFvdfw5HaGHTuy13OsT1FzR\nT6O55Ob/HHpUV9CcEQnR9LvjAy1inOjCNiCg2WD/wb+L6Nrux71HRoG+ZJbdRDH/\n2yGOdvQIqWf1agIEjpVkuGm66QKBgQDhF2rSzkEpJC4lseBnFdrBHr/tkbJYgdks\n7rqJz60aPlLJ+bjblMXW2Tsv1dp1LvPk2jUlwgbOhqz27KWrUTjltJyWpsFi9sBu\nOoS+dZ+3/cgrurfa7e5sw8F7ss6CXLr47xM1iZ3fGbnz2FCUWmh1yyXAszDqwleR\nAgTijmvKswKBgQC15gQq8eIATFLEDQKW1tPsnnkWF/DklyE4K2k0oYqDy+UQAXx7\nzrsqHjr7QbcIkZoZgQhLE9wBDe9yHGoujftAkO03OlLPU7DgW1niN2uja2kfcmhL\nrdOVmLAZrLaQSnSIwgYK3LrDomNoXKS5l1QcNLZNSntuXmghJCLBMbeS4QKBgHWn\nl964kLbAgp6Ra4p2kfF/8TJshZxdwvcJkdeXBhRBn2STc1zTVtYGljlavuWhtTpa\nFI237XbmTmKDL9VsjyECVxcn8s2XzN3RGLG1Kdcyf/7bil6VH5sad3gA7pCVh+W2\nkYPaevqyp9AdsYDaAOARX5pqD5emHb9eHs+NQiqhAoGAUwhvmN0N3wtLlsoROfnB\niv9amzB6esFByLEyPAeLmgHHzbcek96b9+b4VJSu1jvREXj/RKWBTogvwh/ot/QZ\n4t6HgKqyBryUXCH3A8tjIUlPELTvXyeeyax18GKLd45mOMO8Nla/0lxSqvPNpJfH\niil7F8/Jr+EFEzt6IKP8y+0=\n-----END PRIVATE KEY-----\n",
  "client_email": "evw-503@instant-avatar-456707-q7.iam.gserviceaccount.com",
  "client_id": "111783288644374186080",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/evw-503%40instant-avatar-456707-q7.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}

# === Авторизация Google Sheets ===
SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_dict(GOOGLE_CREDENTIALS_JSON, SCOPE)
client = gspread.authorize(creds)
sheet = client.open("azv").sheet1  # Название таблицы

# === FSM Состояния ===
class Register(StatesGroup):
    name = State()
    age = State()

# === Бот и диспетчер ===
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

    # Добавление в таблицу
    sheet.append_row([
        str(message.from_user.id),
        user_data["name"],
        user_data["age"],
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ])

    await message.answer("Спасибо! Ты зарегистрирован ✅")

# === Запуск бота ===
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
