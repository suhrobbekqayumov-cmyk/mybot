import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiohttp import web

# TOKENingizni shu yerga yozing
API_TOKEN = '8784506881:AAETyjPes4Qovme4lBtPuJxIwwaNQABXb94' 

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Render tekin rejimda o'chirib qo'ymasligi uchun server
async def handle(request):
    return web.Response(text="Bot is running!")

async def start_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', int(os.environ.get('PORT', 8080)))
    await site.start()

@dp.message()
async def echo(message: types.Message):
    await message.answer(f"Siz yozdingiz: {message.text}")

async def main():
    # Serverni bot bilan birga ishga tushiramiz
    await start_server()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
