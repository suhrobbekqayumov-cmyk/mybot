import os
import asyncio
import google.generativeai as genai
from aiogram import Bot, Dispatcher, types
from aiohttp import web

# --- KONFIGURATSIYA ---
API_TOKEN = '8784506881:AAE96UbQZj8gnuIc2ydEoxfmo48ZWDuxvpo'
GOOGLE_API_KEY = "AIzaSyBPjfoLuhjq1y2ZoiMR1SJimvAMsmcEsJU"

# Gemini AI sozlash
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# --- RENDER UCHUN WEB SERVER ---
async def handle(request):
    return web.Response(text="Bot is online and running!")

async def start_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get('PORT', 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"Web server {port}-portda ishga tushdi.")

# --- BOT LOGIKASI ---
@dp.message()
async def chat_handler(message: types.Message):
    # /start komandasi uchun
    if message.text == "/start":
        await message.answer("Salom! Men Gemini AI botman. Menga xohlagan savolingizni bering, javob berishga harakat qilaman! ✨")
        return

    # Foydalanuvchiga kutish xabarini ko'rsatish
    wait_msg = await message.answer("O'ylayapman... 🧠")

    try:
        # Gemini-dan javob olish
        response = model.generate_content(message.text)
        
        # Javobni tekshirish va yuborish
        if response and response.text:
            await message.answer(response.text)
        else:
            await message.answer("Kechirasiz, bu savolga javob bera olmayman (xavfsizlik filtri tufayli bo'lishi mumkin).")
            
    except Exception as e:
        # Xatoni aniq tushuntirish
        error_text = str(e)
        if "API key" in error_text:
            await message.answer("Xatolik: Google API kaliti noto'g'ri yoki amal qilish muddati tugagan.")
        else:
            await message.answer(f"Kichik xatolik bo'ldi: {error_text[:100]}...")
    
    # "O'ylayapman" xabarini o'chirib tashlash
    await wait_msg.delete()

# --- ASOSIY ISHGA TUSHIRISH ---
async def main():
    # Parallel ravishda server va botni ishga tushirish
    await start_server()
    print("Bot polling rejimida ish boshladi...")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot to'xtatildi.")
