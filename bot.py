import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.client.session.aiohttp import AiohttpSession
from google import genai
 
import os
 
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
 
 
# Настройка сессии (для обхода локальных ограничений сети при необходимости)
session = AiohttpSession()
session._connector_init = {"ssl": False}
 
bot = Bot(token=TELEGRAM_BOT_TOKEN, session=session)
dp = Dispatcher()
gemini_client = genai.Client(api_key=GEMINI_API_KEY)
 
@dp.message(CommandStart())
async def start_handler(message: types.Message):
    await message.answer(
        "Привет! Я твой персональный ИИ-ассистент по питанию.\n"
        "Учитываю кето-диету и кашрут (без свинины, без смешивания мяса и молока).\n"
        "Напиши состав блюда или продукта для проверки."
    )
 
@dp.message()
async def food_handler(message: types.Message):
    user_text = message.text
    
    # Формируем запрос к Gemini с учетом правил
    prompt = (
        f"Проверь следующий продукт или блюдо: '{user_text}'. "
        "Учти ограничения: кето-диета (высокое содержание жиров, минимум углеводов) "
        "и кашрут (строго без свинины, запрет на смешивание мяса и молока в одном блюде). "
        "Дай короткий вердикт: подходит или нет, и почему."
    )
    
    try:
        response = gemini_client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
        )
        reply_text = response.text
    except Exception as e:
        reply_text = f"Ошибка при обращении к Gemini API: {e}"
 
    await message.answer(reply_text)
 
async def main():
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    print("Бот запущен и ждет сообщения...")
    await dp.start_polling(bot)
 
if __name__ == "__main__":
    asyncio.run(main())
