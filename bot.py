import asyncio
from aiogram import Bot, Dispatcher, F, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, LabeledPrice, PreCheckoutQuery
from aiohttp import web

# ================== НАСТРОЙКИ ==================

BOT_TOKEN = "8355471659:AAFWRNlxYtww9IgEAvwIee0DlWsmExdhJOg"
ADMIN_ID = 5333130126  # Ваш Telegram ID

MAIN_CHANNEL_URL = "https://t.me/+fP9jHqTTGAVkY2Fi"
PRIVATE_CHANNEL_URL = "https://t.me/+GB0H9D7fYN1iOWYy"

CRYPTO_PAY_TOKEN = "526004:AAdTiJf7ebmFVMXm2lFxkud339PdvDgcaly"  # @CryptoBot
PRICE_USD = 2  # Цена приватки

# ================== ТЕКСТЫ ==================

START_TEXT = (
    "Привет. Это Бот-переходник моего канала!\n"
    "В моем канале много интересного контента 🍒\n"
    "Также ты можешь купить приватку ведь в ней я публикую такое.. 🤯\n\n"
    "Hi! This is my channel's Bridge Bot!\n"
    "There’s a lot of exciting content on my channel 🍒\n"
    "You can also buy access to the private channel, because what I post there is just... 🤯"
)

AFTER_BUY_TEXT = (
    "Поздравляю ты купил мою Приватку!\n"
    "Кидай заявку и в скорем времени я приму тебя🍓\n\n"
    "Congrats! You’ve just joined my Private Channel!\n"
    "Send your request, and I’ll accept you soon! 🍓"
)

# ================== КНОПКИ ==================

def start_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("Основной КАНАЛ 🍓", url=MAIN_CHANNEL_URL)],
        [InlineKeyboardButton("Купить Приватку 🍓", callback_data="buy")],
        [InlineKeyboardButton("Переходник", callback_data="bridge")]
    ])

def private_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("Приватка 🍓", url=PRIVATE_CHANNEL_URL)]
    ])

# ================== BOT ==================

bot = Bot(BOT_TOKEN)
dp = Dispatcher()

# ================== СТАРТ ==================

@dp.message(F.text == "/start")
async def start(msg: types.Message):
    await msg.answer(START_TEXT, reply_markup=start_kb())

# ================== ПЕРЕХОДНИК ==================

@dp.callback_query(F.data == "bridge")
async def bridge(cb: types.CallbackQuery):
    await cb.message.answer(START_TEXT, reply_markup=start_kb())
    await cb.answer()

# ================== ПОКУПКА ==================

@dp.callback_query(F.data == "buy")
async def buy(cb: types.CallbackQuery):
    await bot.send_invoice(
        chat_id=cb.from_user.id,
        title="Private Channel 🍓",
        description="Access to private channel",
        payload="private_access",
        provider_token=CRYPTO_PAY_TOKEN,
        currency="USD",
        prices=[LabeledPrice(label="Private Channel", amount=PRICE_USD * 100)]
    )
    await cb.answer()

@dp.pre_checkout_query()
async def pre_checkout(q: PreCheckoutQuery):
    await q.answer(ok=True)

@dp.message(F.successful_payment)
async def payment_done(msg: types.Message):
    await msg.answer(AFTER_BUY_TEXT, reply_markup=private_kb())

# ================== HTTP ДЛЯ UPTIMEROBOT ==================

async def web_server():
    app = web.Application()
    app.router.add_get("/", lambda r: web.Response(text="OK"))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8080)
    await site.start()

# ================== MAIN ==================

async def main():
    await web_server()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
