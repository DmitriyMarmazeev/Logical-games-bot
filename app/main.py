import asyncio

from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from config import BOT_TOKEN

from db import Database

'''БАЗА ДАННЫХ'''

db = Database('./data/database.db')

'''БОТ'''

loop = asyncio.get_event_loop()
bot = Bot(BOT_TOKEN, parse_mode="HTML")

dp = Dispatcher(bot, loop=loop, storage=MemoryStorage())

'''ЗАПУС БОТА'''

if __name__ == "__main__":
    from handlers import dp, send_to_admin
    executor.start_polling(dp, on_startup=send_to_admin, skip_updates=True)
