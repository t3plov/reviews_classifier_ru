import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from app.bot.handlers import *

bot = Bot(token=Config.TG_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=storage)
dp.include_router(router)


async def main():
    """Главная функция запуска бота"""
    print("🤖 Запуск Telegram-бота...")

    # Удаляем вебхук (на случай, если он был установлен ранее)
    await bot.delete_webhook(drop_pending_updates=True)

    # Запускаем polling (бот будет опрашивать Telegram о новых сообщениях)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())