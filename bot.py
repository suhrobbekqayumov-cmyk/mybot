import os
import asyncio
import google.generativeai as genai
from aiogram import Bot, Dispatcher, types
from aiohttp import web

# --- FAQAT SHU IKKI QATORNI TO'G'RI TO'LDIRING ---
API_TOKEN = '8784506881:AAE96UbQZj8gnuIc2ydEoxfmo48ZWDuxvpo'
GOOGLE_API_KEY = "AIzaSyBPjfoLuhjq1y2ZoiMR1SJimvAMsmcEsJU"

# Gemini sozlamalari
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Render uchun kichik server (Port xatosi chiqmasligi uchun)
async def handle(request):
    return web.Response(text="Bot ishlayapti!")

async def start_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get('PORT', 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()

@dp.message()
async def chat(message: types.Message):
    try:
        response = model.generate_content(message.text)
        await message.answer(response.text)
    except:
        await message.answer("Xatolik yuz berdi...")

async def main():
    await start_server()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
