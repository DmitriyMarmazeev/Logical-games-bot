import asyncio
import os
from aiohttp import web

from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from config import BOT_TOKEN

from db import Database

async def health_check(request):
    return web.Response(text="Bot is running")

app = web.Application()
app.add_routes([web.get('/', health_check)])

async def start_webapp():
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, host='0.0.0.0', port=port)
    await site.start()
    print(f"HTTP server started on port {port}")

'''БАЗА ДАННЫХ'''

db = Database('./data/database.db')

'''БОТ'''

loop = asyncio.get_event_loop()
bot = Bot(BOT_TOKEN, parse_mode="HTML")

dp = Dispatcher(bot, loop=loop, storage=MemoryStorage())

'''ЗАПУС БОТА'''

if __name__ == "__main__":
    from handlers import dp, send_to_admin

    if os.getenv("RENDER"):
        loop = asyncio.get_event_loop()
        loop.create_task(start_webapp())
        executor.start_polling(dp, on_startup=send_to_admin, skip_updates=True)
    else:
        executor.start_polling(dp, on_startup=send_to_admin, skip_updates=True)
