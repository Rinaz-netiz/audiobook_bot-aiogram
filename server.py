from aiogram import types, executor
from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.dispatcher.filters import Text
from audio_books import find_audiobooks, first_url, delete_folder
import asyncio
from back import bot, dp


keyword_k = ReplyKeyboardMarkup(resize_keyboard=True).add('Search audiobook')


@dp.message_handler(commands=['start', 'help'])
async def start(message: types.Message):
    await message.answer(f'Hello {message.from_user.full_name}!\n'
                         f'\nThis bot finds any audiobook you want to listen to', reply_markup=keyword_k)


@dp.message_handler(Text(equals='Search audiobook'))
async def wait_book(message: types.Message):
    await message.answer('Enter the book you are interested in', reply_markup=ReplyKeyboardRemove())


@dp.message_handler(lambda message: message.text.startswith('/'))
async def download_audio(message: types.Message):
    await message.answer("Let's start downloading...")
    names = asyncio.create_task(first_url(message.text, message.from_user.id))
    await names
    await delete_folder()
    await bot.send_message(message.from_user.id, "Loading is complete!", reply_markup=keyword_k)


@dp.message_handler()
async def search_audio(message: types.Message):
    books_cor = asyncio.create_task(find_audiobooks(message.text))
    books = await books_cor
    await bot.send_message(message.from_user.id, f'Found books: '
                                                 f'\n{books}')


executor.start_polling(dp, skip_updates=True)
