from aiogram import Bot, Dispatcher
import os

TOKEN = os.getenv("TELEGRAM_API_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
