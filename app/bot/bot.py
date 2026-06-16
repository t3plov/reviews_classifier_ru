import asyncio
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from config import Config

# Инициализация бота и диспетчера
bot = Bot(token=Config.TG_TOKEN)
dp = Dispatcher()

# URL твоего FastAPI сервера
API_URL = f"http://{Config.FAST_API_HOST}:{Config.FAST_API_PORT}/predict"


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Обработчик команды /start"""
    await message.answer(
        "👋 Привет! Я бот для анализа тональности отзывов.\n\n"
        "Просто отправь мне текст отзыва, и я скажу, какой он: "
        "позитивный, негативный или нейтральный."
    )


@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    """Обработчик команды /help"""
    await message.answer(
        "📖 Как пользоваться:\n\n"
        "1. Отправь мне текст отзыва (например, 'Фильм просто отличный!')\n"
        "2. Я проанализирую его и верну тональность\n"
        "3. Также покажу уверенность модели в предсказании\n\n"
        "Команды:\n"
        "/start - Начать работу\n"
        "/help - Показать справку"
    )


@dp.message()
async def analyze_sentiment(message: types.Message):
    """Обработчик любого текстового сообщения"""
    # Получаем текст от пользователя
    text = message.text

    if not text or len(text.strip()) == 0:
        await message.answer("Пожалуйста, отправьте текстовый отзыв.")
        return

    # Отправляем запрос к FastAPI
    try:
        async with aiohttp.ClientSession() as session:
            payload = {"text": text}

            async with session.post(API_URL, json=payload) as response:
                if response.status == 200:
                    result = await response.json()

                    # Форматируем красивый ответ
                    label = result["label"]
                    confidence = result["confidence"]
                    confidence_percent = confidence * 100

                    response_text = (
                        f"📊 **Результат анализа:**\n\n"
                        f"🏷 **Тональность:** {label}\n"
                        f"📈 **Уверенность модели:** {confidence_percent:.2f}%\n\n"
                        f"📝 **Текст:** {text[:100]}{'...' if len(text) > 100 else ''}"
                    )

                    await message.answer(response_text, parse_mode="Markdown")
                else:
                    error_data = await response.json()
                    await message.answer(
                        f"❌ Ошибка при обработке: {error_data.get('detail', 'Неизвестная ошибка')}"
                    )

    except aiohttp.ClientError as e:
        await message.answer(
            "❌ Не удалось подключиться к серверу анализа. "
            "Убедитесь, что FastAPI сервер запущен (python run.py)."
        )
    except Exception as e:
        await message.answer(f"❌ Произошла ошибка: {str(e)}")


async def main():
    """Главная функция запуска бота"""
    print("🤖 Запуск Telegram-бота...")
    print(f"API URL: {API_URL}")

    # Удаляем вебхук (на случай, если он был установлен ранее)
    await bot.delete_webhook(drop_pending_updates=True)

    # Запускаем polling (бот будет опрашивать Telegram о новых сообщениях)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())