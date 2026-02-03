import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message, InlineKeyboardMarkup, InlineKeyboardButton,
    LabeledPrice, PreCheckoutQuery
)
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiohttp import web

# ================== НАСТРОЙКИ ==================

BOT_TOKEN = "8355471659:AAFWRNlxYtww9IgEAvwIee0DlWsmExdhJOg"
ADMIN_ID = 5333130126 # твой Telegram ID

MAIN_CHANNEL_URL = "https://t.me/+fP9jHqTTGAVkY2Fi"
PRIVATE_CHANNEL_URL = "https://t.me/+GB0H9D7fYN1iOWYy"

CRYPTO_PAY_TOKEN = "526004:AAdTiJf7ebmFVMXm2lFxkud339PdvDgcaly"  # @CryptoBot → /pay → API Token
PRICE_USD = 2

# ================== ТЕКСТЫ ==================

START_TEXT = (
    "Привет. Это Бот-переходник моего канала!\n"
    "В моем канале много интересного контента 🍒\n"
    "Также ты можешь купить приватку ведь в ней я публикую такое.. 🤯\n\n"
    "———————\n\n"
    "Hi! This is my channel's Bridge Bot!\n"
    "There’s a lot of exciting content on my channel 🍒\n"
    "You can also buy access to the private channel, because what I post there is just... 🤯"
)

AFTER_BUY_TEXT = (
    "Поздравляю ты купил мою Приватку!\n"
    "Кидай заявку и в скорем времени я приму тебя🍓\n\n"
    "———————\n\n"
    "Congrats! You’ve just joined my Private Channel!\n"
    "Send your request, and I’ll accept you soon! 🍓"
)

# ================== КНОПКИ ==================

def start_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Основной КАНАЛ 🍓", url=MAIN_CHANNEL_URL)],
        [InlineKeyboardButton(text="Купить Приватку 🍓", callback_data="buy")]
    ])

def private_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Приватка 🍓", url=PRIVATE_CHANNEL_URL)]
    ])

# ================== FSM ==================

class Broadcast(StatesGroup):
    waiting = State()

# ================== BOT ==================

bot = Bot(BOT_TOKEN)
dp = Dispatcher()

USERS = set()  # временно в RAM

# ================== START ==================

@dp.message(Command("start"))
async def start(msg: Message):
    USERS.add(msg.from_user.id)
    await msg.answer(START_TEXT, reply_markup=start_kb())

# ================== BUY ==================

@dp.callback_query(F.data == "buy")
async def buy(cb):
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
async def success(msg: Message):
    await msg.answer(AFTER_BUY_TEXT, reply_markup=private_kb())

# ================== ADMIN ==================

@dp.message(Command("admin"))
async def admin(msg: Message, state: FSMContext):
    if msg.from_user.id != ADMIN_ID:
        return
    await msg.answer("Отправь сообщение для рассылки")
    await state.set_state(Broadcast.waiting)

@dp.message(Broadcast.waiting)
async def broadcast(msg: Message, state: FSMContext):
    if msg.from_user.id != ADMIN_ID:
        return

    sent = 0
    for uid in USERS:
        try:
            await msg.copy_to(uid)
            sent += 1
        except:
            pass

    await msg.answer(f"Рассылка завершена. Отправлено: {sent}")
    await state.clear()

# ================== UPTIME ROBOT ==================

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
