import os
import asyncio
import edge_tts
import google.generativeai as genai
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiohttp import web

# --- SOZLAMALAR ---
API_TOKEN = '8784506881:AAGde52AFefql6co4HU0il5AgRas3XYa3xI' # O'zingizniki tursin
GOOGLE_API_KEY = "AIzaSyD0wUMpVz8pShFcJJkm8tKL9NInLlc8z7M" # Gemini API keyingizni qo'ying

# Gemini AI ulanishi
try:
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
except:
    model = None

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
USER_LANGS = {}

# --- RENDER UCHUN SERVER ---
async def handle(request):
    return web.Response(text="Bot is running!")

async def start_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', int(os.environ.get('PORT', 8080)))
    await site.start()

# --- TUGMALAR ---
def get_langs_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(text="🇺🇿 O'zbek", callback_data="setlang_uz"),
        types.InlineKeyboardButton(text="🇷🇺 Rus", callback_data="setlang_ru"),
        types.InlineKeyboardButton(text="🇺🇸 Ingliz", callback_data="setlang_en")
    )
    return builder.as_markup()

# --- HANDLERLAR ---
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    USER_LANGS[message.from_user.id] = 'uz'
    await message.answer(
        "Xush kelibsiz! ✨\nTilni tanlang va menga xabar yuboring:",
        reply_markup=get_langs_keyboard()
    )

@dp.callback_query(F.data.startswith("setlang_"))
async def change_language(call: types.CallbackQuery):
    lang_code = call.data.split("_")[1]
    USER_LANGS[call.from_user.id] = lang_code
    
    msg = {"uz": "Til O'zbekcha! 🇺🇿", "ru": "Язык Русский! 🇷🇺", "en": "Language English! 🇺🇸"}
    await call.answer(msg.get(lang_code))
    await call.message.edit_text(f"✅ {msg.get(lang_code)}\nEndi biron narsa yozing...")

@dp.message()
async def ai_handler(message: types.Message):
    user_id = message.from_user.id
    lang = USER_LANGS.get(user_id, 'uz')
    wait_msg = await message.answer("O'ylayapman... 🧠")

    try:
        # AI javobi
        prompt = f"Answer only in {lang} language: {message.text}"
        response = model.generate_content(prompt)
        reply_text = response.text
        await message.answer(reply_text)

        # Ovoz chiqarish
        v_map = {'uz': "uz-UZ-MadinaNeural", 'ru': "ru-RU-SvetlanaNeural", 'en': "en-US-GuyNeural"}
        v_file = f"voice_{user_id}.mp3"
        c = edge_tts.Communicate(reply_text[:300], v_map.get(lang, "uz-UZ-MadinaNeural"))
        await c.save(v_file)
        await message.answer_voice(types.FSInputFile(v_file))
        os.remove(v_file)
    except:
        await message.answer("Xato! API keyni tekshiring.")
    await wait_msg.delete()

async def main():
    await start_server()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
