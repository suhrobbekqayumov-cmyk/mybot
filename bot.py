import os
import asyncio
import edge_tts
import google.generativeai as genai
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiohttp import web

# --- SOZMALAR ---
API_TOKEN = '8784506881:AAFMP9ZtR0DAu9OhSeV2v3UeqT2-rAkiak' 
GOOGLE_API_KEY = "AIzaSyBPjfoLuhjq1y2ZoiMR1SJimvAMsmcEsJU"

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
    # Render portni 10000 yoki 8080 orqali qidiradi
    port = int(os.environ.get('PORT', 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
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
        prompt = f"Answer only in {lang} language: {message.text}"
        response = model.generate_content(prompt)
        reply_text = response.text
        await message.answer(reply_text)

        v_map = {'uz': "uz-UZ-MadinaNeural", 'ru': "ru-RU-SvetlanaNeural", 'en': "en-US-GuyNeural"}
        v_file = f"voice_{user_id}.mp3"
        c = edge_tts.Communicate(reply_text[:300], v_map.get(lang, "uz-UZ-MadinaNeural"))
        await c.save(v_file)
        await message.answer_voice(types.FSInputFile(v_file))
        os.remove(v_file)
    except Exception as e:
        await message.answer(f"Xato! API keyni yoki ulanishni tekshiring.")
    
    await wait_msg.delete()

async def main():
    # Server va botni parallel yurgizish
    await start_server()
    print("Server ishga tushdi, polling boshlanmoqda...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
