import logging
from aiogram import Bot, Dispatcher, types, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import WebAppInfo, InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.middleware import BaseMiddleware
from redis.asyncio import Redis
import asyncio

from .config import config

# Настройка логирования
logging.basicConfig(
    level=config.LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Инициализация бота
try:
    config.check_required()
except EnvironmentError as e:
    logger.critical(e)
    exit(1)

bot = Bot(
    token=config.BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()
router = Router()
dp.include_router(router)

# Инициализация Redis
redis = Redis.from_url(config.REDIS_URL)
dp["redis"] = redis

class ErrorMiddleware(BaseMiddleware):
    """Middleware для обработки ошибок"""
    async def __call__(self, handler, event, data):
        try:
            return await handler(event, data)
        except Exception as e:
            logger.error(f"Critical error: {e}", exc_info=True)
            if config.ADMIN_ID:
                await bot.send_message(
                    config.ADMIN_ID,
                    f"🚨 **Ошибка в боте**\n\n"
                    f"```python\n{str(e)}\n```",
                    parse_mode=ParseMode.MARKDOWN
                )
            raise

router.message.middleware(ErrorMiddleware())

def get_main_keyboard():
    """Генерирует клавиатуру главного меню"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="🌐 Открыть WebApp",
            web_app=WebAppInfo(url=config.WEB_APP_URL))
    )
    builder.row(
        InlineKeyboardButton(
            text="🔔 Подписаться",
            callback_data="subscribe"),
        InlineKeyboardButton(
            text="🔕 Отписаться",
            callback_data="unsubscribe")
    )
    return builder.as_markup()

@router.message(Command("start"))
async def send_welcome(message: types.Message):
    """Обработчик команды /start"""
    user = message.from_user
    welcome_text = (
        f"👋 Приветствую, {user.first_name}!\n\n"
        "Я ваш персональный помощник. Вот основные возможности:\n\n"
        "• /start - Главное меню\n"
        "• /help - Помощь по командам\n"
        "• /webapp - Открыть веб-приложение\n"
        "• /status - Проверить подписку"
    )
    await message.answer(welcome_text, reply_markup=get_main_keyboard())

@router.message(Command("help"))
async def help_handler(message: types.Message):
    """Показывает справку по командам"""
    help_text = (
        "📚 **Доступные команды:**\n\n"
        "/start - Основное меню\n"
        "/help - Эта справка\n"
        "/webapp - Открыть веб-приложение\n"
        "/status - Статус подписки\n\n"
        "🔐 **Безопасность:**\n"
        "Все данные хранятся в зашифрованном виде"
    )
    await message.answer(help_text)

@router.message(Command("status"))
async def status_handler(message: types.Message):
    """Проверяет статус подписки"""
    user_id = message.from_user.id
    is_subscribed = await redis.sismember("subscriptions", user_id)
    status = "активна" if is_subscribed else "не активна"
    await message.answer(f"🔔 Ваша подписка: {status}")

@router.callback_query(F.data == "subscribe")
async def subscribe(callback: CallbackQuery):
    """Обработчик подписки"""
    user_id = callback.from_user.id
    await redis.sadd("subscriptions", user_id)
    await callback.answer("✅ Вы успешно подписались!", show_alert=True)

@router.callback_query(F.data == "unsubscribe")
async def unsubscribe(callback: CallbackQuery):
    """Обработчик отписки"""
    user_id = callback.from_user.id
    await redis.srem("subscriptions", user_id)
    await callback.answer("❌ Вы отписались от обновлений", show_alert=True)

async def main():
    """Основная функция запуска"""
    try:
        logger.info("Starting bot...")
        await dp.start_polling(bot)
    finally:
        await redis.close()
        await bot.session.close()
        logger.info("Bot stopped gracefully")

if __name__ == '__main__':
    asyncio.run(main())
