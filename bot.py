import os
import asyncio
import google.generativeai as genai
from aiogram import Bot, Dispatcher, types
from aiohttp import web

# --- TO'G'RI TO'LDIRILGAN ---
API_TOKEN = '8784506881:AAE96UbQZj8gnuIc2ydEoxfmo48ZWDuxvpo'
GOOGLE_API_KEY = "AIzaSyBPjfoLuhjq1y2ZoiMR1SJimvAMsmcEsJU"

# Gemini sozlamalari
genai.configure(api_key=GOOGLE_API_KEY)
# Bu yerda modelni to'g'ri chaqirish
model = genai.GenerativeModel('gemini-1.5-flash')

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Render uchun server
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
    # Agar foydalanuvchi /start bossa
    if message.text == "/start":
        await message.answer("Salom! Men Gemini AI botman. Savolingizni bering!")
        return

    try:
        # AI dan javob olish
        response = model.generate_content(message.text)
        if response.text:
            await message.answer(response.text)
        else:
            await message.answer("AI hozircha javob bera olmadi, qaytadan urinib ko'ring.")
    except Exception as e:
        # Xatoni aniq ko'rish uchun
        await message.answer(f"Xatolik tafsiloti: {str(e)}")

async def main():
    await start_server()
    print("Bot polling boshladi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
