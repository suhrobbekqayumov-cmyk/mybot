import asyncio
import logging
import wikipedia
import os
import edge_tts
import google.generativeai as genai
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

# --- SOZLAMALAR ---
API_TOKEN ="8784506881:AAETyjPes4Qovme4lBtPuJxIwwaNQABXb94"

# DIQQAT: Mana bu yerga o'zingizning Gemini API kalitingizni qo'ying!
# Uni https://aistudio.google.com/ saytidan tekinga olishingiz mumkin.
GOOGLE_API_KEY = "SIZ_OLGAN_GEMINI_KEY"

try:
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    print(f"Gemini ulanishda xato: {e}")
    model = None

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()
USER_LANGS = {}


# --- TUGMALAR ---
def get_main_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(text="🇺🇿 O'zbek", callback_data="lang_uz"),
        types.InlineKeyboardButton(text="🇷🇺 Rus", callback_data="lang_ru"),
        types.InlineKeyboardButton(text="🇺🇸 Ingliz", callback_data="lang_en")
    )
    return builder.as_markup()


# --- HANDLERLAR ---
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    USER_LANGS[message.from_user.id] = 'uz'
    await message.answer("Xush kelibsiz! ✨\nMen Wikipedia, AI va Tarjimon botman.\n\n"
                         "Menga biron so'zni yozing (masalan: 'Olma tarjimasi')",
                         reply_markup=get_main_keyboard())


@dp.message()
async def main_handler(message: types.Message):
    msg_text = message.text.lower().strip()
    user_id = message.from_user.id
    lang = USER_LANGS.get(user_id, 'uz')

    # 1. TARJIMON FILTRI (Aniqroq ishlashi uchun)
    if "tarjimasi" in msg_text:
        if not model:
            await message.answer("Xato: Gemini API kaliti ulanmagan! ❌")
            return

        wait_msg = await message.answer("Tarjima qilyapman... 🔄")
        # "tarjimasi" so'zini olib tashlab, qolgan so'zni tarjima qilamiz
        word = msg_text.replace("tarjimasi", "").strip()

        try:
            prompt = f"Translate the word or phrase '{word}' to English. Give ONLY the translated English result, no extra text."
            ai_res = model.generate_content(prompt)
            translation = ai_res.text.strip()

            await message.answer(f"🇺🇿 Matn: {word}\n🇺🇸 Inglizcha: **{translation}**", parse_mode="Markdown")

            # Inglizcha ovoz (Guy ovozi)
            v_name = f"v_en_{user_id}.mp3"
            c = edge_tts.Communicate(translation, "en-US-GuyNeural")
            await c.save(v_name)
            await message.answer_voice(types.FSInputFile(v_name))
            os.remove(v_name)
        except Exception as e:
            await message.answer(f"Tarjimada xato: {e}")

        await wait_msg.delete()
        return

    # 2. SALOMLASHISH
    salom_list = ['salom', 'assalomu alaykum', 'asalomu alaykum', 'hi', 'hello']
    if any(s == msg_text for s in salom_list):
        javob = "Valaykum assalom! Sizga qanday yordam bera olaman? 😊"
        await message.answer(javob)
        v_name = f"v_salom_{user_id}.mp3"
        c = edge_tts.Communicate(javob, "uz-UZ-MadinaNeural")
        await c.save(v_name)
        await message.answer_voice(types.FSInputFile(v_name))
        os.remove(v_name)
        return

    # 3. WIKIPEDIA / AI QIDIRUV
    wait_msg = await message.answer("Qidiryapman... 🔍")
    try:
        wikipedia.set_lang(lang)
        page = wikipedia.page(msg_text)
        summary = wikipedia.summary(msg_text, sentences=2)

        img_url = next((i for i in page.images if i.lower().endswith(('.jpg', '.png', '.jpeg'))), None)
        if img_url:
            await message.answer_photo(img_url, caption=f"🔍 Wikipedia: {page.title}")

        kb = InlineKeyboardBuilder()
        kb.row(types.InlineKeyboardButton(text="🔗 To'liq o'qish", url=page.url))
        await message.answer(summary, reply_markup=kb.as_markup())
        final_text = summary
    except:
        if model:
            ai_res = model.generate_content(f"Javob bering ({lang} tilida): {msg_text}")
            await message.answer(f"🤖 AI:\n\n{ai_res.text}")
            final_text = ai_res.text[:300]
        else:
            await message.answer("Ma'lumot topilmadi. ❌")
            await wait_msg.delete()
            return

    # Ovozli javob
    try:
        v_map = {'uz': "uz-UZ-MadinaNeural", 'ru': "ru-RU-SvetlanaNeural", 'en': "en-US-GuyNeural"}
        v_file = f"v_res_{user_id}.mp3"
        c = edge_tts.Communicate(final_text[:300], v_map.get(lang, "uz-UZ-MadinaNeural"))
        await c.save(v_file)
        await message.answer_voice(types.FSInputFile(v_file))
        os.remove(v_file)
    except:
        pass

    await wait_msg.delete()


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
