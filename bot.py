import requests

import asyncio
from web3 import Web3
from aiogram import Bot, Dispatcher
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import Command
import config

bot = Bot(token=config.TOKEN)
dp = Dispatcher()

user_settings = {}
menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🚀 Signal"), KeyboardButton(text="📊 Market")],
        [KeyboardButton(text="⚙️ Settings"), KeyboardButton(text="👤 My Settings")],
        [KeyboardButton(text="🐋 Whale")], [KeyboardButton(text="🛑 Stop")]
    ],
    resize_keyboard=True
)
CHAT_ID = None
CHANNEL_ID = "@skibidi_trade_signals"
SMART_WALLETS = {
    "Justin Sun": "0x3ddfa8ec3052539b6c9549f12cea2c295cff5296",
    "Vitalik Buterin": "0xd8da6bf26964af9d7eed9e03e53415d37aa96045"
}
ETHERSCAN_API = "IIFCPF7DH7NJ7QWYAG6DEBM98Y86SYG14J"



@dp.message(Command("start"))
async def start_handler(message: Message):
    global CHAT_ID
    CHAT_ID = message.chat.id

    await message.answer(
    "Бот работает 🚀",
    reply_markup=menu
)

@dp.message(Command("signal"))
async def signal_handler(message: Message):

    url = "https://api.binance.com/api/v3/ticker/24hr?symbol=BTCUSDT"

    data = requests.get(url).json()

    price_change = float(data["priceChangePercent"])
    current_price = data["lastPrice"]

    if price_change > 0:
        signal = "BUY 📈"
        trend = "BULLISH 🟢"
    else:
        signal = "SELL 📉"
        trend = "BEARISH 🔴"

    text = f"""
🚀 BTC SIGNAL

💰 Цена: ${current_price}

📊 Изменение 24ч: {price_change}%

📈 Тренд: {trend}

🔥 Сигнал: {signal}
"""

    await message.answer(text)

@dp.message(Command("btc"))
async def btc_price(message: Message):

    url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"

    data = requests.get(url).json()

    price = data["price"]

    await message.answer(f"BTC сейчас: ${price}")

@dp.message(Command("settings"))
async def settings_handler(message: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="BTC", callback_data="coin_BTC"),
            InlineKeyboardButton(text="ETH", callback_data="coin_ETH"),
        ],
        [
            InlineKeyboardButton(text="SOL", callback_data="coin_SOL"),
            InlineKeyboardButton(text="XRP", callback_data="coin_XRP"),
        ]
    ])

    await message.answer("Выбери монету для авто-сигналов:", reply_markup=keyboard)


@dp.callback_query(lambda c: c.data.startswith("coin_"))
async def choose_coin(callback: CallbackQuery):
    user_id = callback.from_user.id
    coin = callback.data.replace("coin_", "")

    user_settings[user_id] = {
        "chat_id": callback.message.chat.id,
        "coin": coin,
        "interval": 1800,
        "last_sent": 0
    }

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="30 минут", callback_data="interval_1800"),
            InlineKeyboardButton(text="1 час", callback_data="interval_3600"),
        ],
        [
            InlineKeyboardButton(text="3 часа", callback_data="interval_10800"),
            InlineKeyboardButton(text="6 часов", callback_data="interval_21600"),
        ]
    ])

    await callback.message.answer(
        f"Монета выбрана: {coin}\nТеперь выбери интервал:",
        reply_markup=keyboard
    )


@dp.callback_query(lambda c: c.data.startswith("interval_"))
async def choose_interval(callback: CallbackQuery):
    user_id = callback.from_user.id
    interval = int(callback.data.replace("interval_", ""))

    if user_id not in user_settings:
        await callback.message.answer("Сначала выбери монету через /settings")
        return

    user_settings[user_id]["interval"] = interval

    minutes = interval // 60

    await callback.message.answer(
        f"✅ Готово!\nАвто-сигналы будут приходить по {user_settings[user_id]['coin']} каждые {minutes} минут."
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="BTC", callback_data="coin_BTC"),
            InlineKeyboardButton(text="ETH", callback_data="coin_ETH"),
        ],
        [
            InlineKeyboardButton(text="SOL", callback_data="coin_SOL"),
            InlineKeyboardButton(text="XRP", callback_data="coin_XRP"),
        ]
    ])

    await message.answer("Выбери монету для авто-сигналов:", reply_markup=keyboard)


@dp.callback_query(lambda c: c.data.startswith("coin_"))
async def choose_coin(callback: CallbackQuery):
    user_id = callback.from_user.id
    coin = callback.data.replace("coin_", "")

    user_settings[user_id] = {
        "chat_id": callback.message.chat.id,
        "coin": coin,
        "interval": 1800,
        "last_sent": 0
    }

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="30 минут", callback_data="interval_1800"),
            InlineKeyboardButton(text="1 час", callback_data="interval_3600"),
        ],
        [
            InlineKeyboardButton(text="3 часа", callback_data="interval_10800"),
            InlineKeyboardButton(text="6 часов", callback_data="interval_21600"),
        ]
    ])

    await callback.message.answer(
        f"Монета выбрана: {coin}\nТеперь выбери интервал:",
        reply_markup=keyboard
    )


@dp.callback_query(lambda c: c.data.startswith("interval_"))
async def choose_interval(callback: CallbackQuery):
    user_id = callback.from_user.id
    interval = int(callback.data.replace("interval_", ""))

    if user_id not in user_settings:
        await callback.message.answer("Сначала выбери монету через /settings")
        return

    user_settings[user_id]["interval"] = interval

    minutes = interval // 60

    await callback.message.answer(
        f"✅ Готово!\nАвто-сигналы будут приходить по {user_settings[user_id]['coin']} каждые {minutes} минут."
    )
async def coin_signal(message: Message, symbol: str, name: str):
    url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}USDT"

    data = requests.get(url).json()

    price_change = float(data["priceChangePercent"])
    current_price = data["lastPrice"]

    if price_change > 0:
        signal = "BUY 📈"
        trend = "BULLISH 🟢"
    else:
        signal = "SELL 📉"
        trend = "BEARISH 🔴"

    text = f"""
🚀 {name} SIGNAL

💰 Цена: ${current_price}
📊 Изменение 24ч: {price_change}%
📈 Тренд: {trend}

🔥 Сигнал: {signal}
"""

    await message.answer(text)


@dp.message(Command("eth"))
async def eth_signal(message: Message):
    await coin_signal(message, "ETH", "ETH")


@dp.message(Command("sol"))
async def sol_signal(message: Message):
    await coin_signal(message, "SOL", "SOL")


@dp.message(Command("xrp"))
async def xrp_signal(message: Message):
    await coin_signal(message, "XRP", "XRP")

@dp.message(Command("market"))
async def market_signal(message: Message):
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,solana,ripple&vs_currencies=usd&include_24hr_change=true"
    data = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}).json()

    coins = {
        "BTC": "bitcoin",
        "ETH": "ethereum",
        "SOL": "solana",
        "XRP": "ripple"
    }

    text = "📊 ОБЗОР РЫНКА\n\n"

    for symbol, coin_id in coins.items():
        item = data.get(coin_id)

        if not item:
            text += f"❌ {symbol}: нет данных\n\n"
            continue

        price = round(item.get("usd", 0), 4)
        change = round(item.get("usd_24h_change", 0), 3)

        if change > 0:
            trend = "BULLISH 🟢"
            signal = "BUY 📈"
        else:
            trend = "BEARISH 🔴"
            signal = "SELL 📉"

        text += f"""
🚀 {symbol}

💰 Цена: ${price}
📊 24ч: {change}%
📈 Тренд: {trend}
🔥 Сигнал: {signal}

"""

    await bot.send_message(CHANNEL_ID, text)
    await message.answer(text)
    coins = ["BTC", "ETH", "SOL", "XRP"]

@dp.message(Command("settings"))
async def settings_handler(message: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="BTC", callback_data="coin_BTC"),
            InlineKeyboardButton(text="ETH", callback_data="coin_ETH"),
        ],
        [
            InlineKeyboardButton(text="SOL", callback_data="coin_SOL"),
            InlineKeyboardButton(text="XRP", callback_data="coin_XRP"),
        ]
    ])

    await message.answer("Выбери монету для авто-сигналов:", reply_markup=keyboard)



@dp.callback_query(lambda c: c.data.startswith("coin_"))
async def choose_coin(callback: CallbackQuery):
    user_id = callback.from_user.id
    coin = callback.data.replace("coin_", "")

    user_settings[user_id] = {
        "chat_id": callback.message.chat.id,
        "coin": coin,
        "interval": 1800,
        "last_sent": 0
    }

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="30 минут", callback_data="interval_1800"),
            InlineKeyboardButton(text="1 час", callback_data="interval_3600"),
        ],
        [
            InlineKeyboardButton(text="3 часа", callback_data="interval_10800"),
            InlineKeyboardButton(text="6 часов", callback_data="interval_21600"),
        ]
    ])

    await callback.message.answer(
        f"Монета выбрана: {coin}\nТеперь выбери интервал:",
        reply_markup=keyboard
    )


@dp.callback_query(lambda c: c.data.startswith("interval_"))
async def choose_interval(callback: CallbackQuery):
    user_id = callback.from_user.id
    interval = int(callback.data.replace("interval_", ""))

    if user_id not in user_settings:
        await callback.message.answer("Сначала выбери монету через /settings")
        return

    user_settings[user_id]["interval"] = interval

    minutes = interval // 60

    await callback.message.answer(
        f"✅ Готово!\nАвто-сигналы будут приходить по {user_settings[user_id]['coin']} каждые {minutes} минут."
    )

@dp.message(Command("mysettings"))
async def my_settings(message: Message):
    user_id = message.from_user.id

    if user_id not in user_settings:
        await message.answer("У тебя ещё нет настроек. Напиши /settings")
        return

    settings = user_settings[user_id]

    minutes = settings["interval"] // 60
    coin = settings["coin"]

    await message.answer(
        f"⚙️ Твои настройки:\n\n"
        f"🪙 Монета: {coin}\n"
        f"⏰ Интервал: {minutes} минут"
    )


@dp.message(Command("stop"))
async def stop_signals(message: Message):
    user_id = message.from_user.id

    if user_id in user_settings:
        del user_settings[user_id]
        await message.answer("⛔ Авто-сигналы отключены.")
    else:
        await message.answer("У тебя и так нет активных авто-сигналов.")

@dp.message(Command("help"))
async def help_handler(message: Message):
    text = """
🤖 Skibidi Trade Signals

Команды:

/start — запустить бота
/settings — выбрать монету и интервал авто-сигналов
/mysettings — посмотреть свои настройки
/stop — отключить авто-сигналы

/signal — сигнал по BTC
/btc — цена BTC
/eth — сигнал по ETH
/sol — сигнал по SOL
/xrp — сигнал по XRP
/market — обзор рынка
"""
    await message.answer(text)

@dp.message(Command("market"))
async def market_overview(message: Message):

    coins = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT"]

    text = "📊 Обзор рынка:\n\n"

    for symbol in coins:

        url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"

        data = requests.get(url).json()

        price = float(data["lastPrice"])
        change = float(data["priceChangePercent"])

        if change >= 0:
            emoji = "🟢"
        else:
            emoji = "🔴"

        coin = symbol.replace("USDT", "")

        text += (
            f"{emoji} {coin}\n"
            f"💲 Цена: ${price:.2f}\n"
            f"📈 24ч: {change:.2f}%\n\n"
        )

    await message.answer(text)

@dp.message(lambda message: message.text == "📊 Market")
async def market_button(message: Message):
    await market_signal(message)


@dp.message(lambda message: message.text == "🚀 Signal")
async def signal_button(message: Message):
    await signal_handler(message)


@dp.message(lambda message: message.text == "⚙️ Settings")
async def settings_button(message: Message):
    await settings_handler(message)


@dp.message(lambda message: message.text == "👤 My Settings")
async def mysettings_button(message: Message):
    await my_settings(message)


@dp.message(lambda message: message.text == "🛑 Stop")
async def stop_button(message: Message):
    await stop_signals(message)

@dp.message(Command("wallet"))
async def wallet_info(message: Message):

    text = f"""
🐋 Smart Money Wallet

📌 Адрес:
{SMART_WALLET}

🔍 Etherscan:
https://etherscan.io/address/{SMART_WALLET}
"""

    await message.answer(text)

@dp.message(Command("whale"))
async def whale_alert(message: Message):

    SMART_WALLETS = {
        "Justin Sun": "0x3ddfa8ec3052539b6c9549f12cea2c295cff5296",
        "Vitalik": "0xd8da6bf26964af9d7eed9e03e53415d37aa96045"
    }

    text = "🐋 SMART MONEY TRANSFERS\n\n"

    for owner, wallet in SMART_WALLETS.items():

        url = f"https://api.etherscan.io/v2/api?chainid=1&module=account&action=tokentx&address={wallet}&page=1&offset=5&sort=desc&apikey={ETHERSCAN_API}"

        data = requests.get(url).json()

        if data["status"] != "1":
            continue

        for tx in data["result"][:5]:

            token = tx["tokenSymbol"]

            ALLOWED_TOKENS = ["ETH", "WETH", "USDT", "USDC", "WBTC", "PEPE", "SHIB", "LINK", "UNI"]

            if token not in ALLOWED_TOKENS:
                continue

            value = int(tx["value"])
            decimals = int(tx["tokenDecimal"])

            real_value = value / (10 ** decimals)

            if real_value < 1000:
                continue

            signal = "BUY 📈"

            if tx["to"].lower() != wallet.lower():
                signal = "SELL 📉"

            text += f"""
🐋 {owner}

🪙 Монета: {token}
💰 Объём: ${round(real_value, 2)}
🔥 Сигнал: {signal}

"""

    if text == "🐋 SMART MONEY TRANSFERS\n\n":
        text += "Пока нет свежих крупных сделок ✅"

    if "🪙" in text:
        await bot.send_message(CHANNEL_ID, text)

    await message.answer(text)

@dp.message(lambda message: message.text == "🐋 Whale")
async def whale_button(message: Message):
    await whale_alert(message)

async def main():
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

