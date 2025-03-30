import logging
from aiogram import Bot, Dispatcher, types, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import WebAppInfo, InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
import asyncio

# Настройки
API_TOKEN = ''
WEB_APP_URL = ''
SUBSCRIPTIONS = set()  # Временное хранилище (замените на БД)

# Инициализация
logging.basicConfig(level=logging.INFO)
bot = Bot(
    token=API_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
router = Router()
dp.include_router(router)

def get_main_keyboard():
    """Генерирует основную клавиатуру"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="🌐 Открыть WebApp",
            web_app=WebAppInfo(url=WEB_APP_URL)))
    builder.row(
        InlineKeyboardButton(
            text="🔔 Подписаться",
            callback_data="subscribe"),
        InlineKeyboardButton(
            text="🔕 Отписаться",
            callback_data="unsubscribe"))
    return builder.as_markup()

@router.message(Command("start"))
async def send_welcome(message: types.Message):
    """Обработчик команды /start"""
    user = message.from_user
    welcome_text = (
        f"👋 Добро пожаловать, {user.first_name}!\n"
        "Я ваш персональный помощник. Вот что я умею:\n\n"
        "🔹 <b>Основные команды:</b>\n"
        "/help - Получить справку по всем командам\n"
        "/auth - Показать данные профиля\n"
        "/webapp - Открыть веб-приложение\n\n"
        "🔹 <b>Уведомления:</b>\n"
        "Используй кнопки ниже для управления подписками"
    )
    await message.answer(welcome_text, reply_markup=get_main_keyboard())

@router.message(Command("help"))
async def help_handler(message: types.Message):
    """Подробная справка по командам"""
    help_text = (
        "📚 <b>Полный список команд:</b>\n\n"
        "<code>/start</code> - Основное меню бота\n"
        "<code>/help</code> - Эта справка\n"
        "<code>/auth</code> - Показать ваши данные авторизации\n"
        "<code>/webapp</code> - Открыть веб-интерфейс\n\n"
        "🔸 <b>Управление подписками:</b>\n"
        "Используйте кнопки 'Подписаться/Отписаться' в меню\n\n"
        "🔸 <b>Примеры использования:</b>\n"
        "Чтобы открыть веб-приложение, нажмите:\n"
        "<code>/webapp</code> или кнопку в меню"
    )
    await message.answer(help_text)

@router.message(Command("auth"))
async def auth_handler(message: types.Message):
    """
    Показывает данные авторизации через Telegram
    Фактическая авторизация происходит автоматически при первом взаимодействии с ботом
    """
    user = message.from_user
    auth_text = (
        "🔑 <b>Ваши данные для авторизации:</b>\n\n"
        f"🆔 <b>Telegram ID:</b> <code>{user.id}</code>\n"
        f"👤 <b>Имя:</b> {user.first_name}\n"
        f"📛 <b>Фамилия:</b> {user.last_name or 'не указана'}\n"
        f"📱 <b>Юзернейм:</b> @{user.username or 'не установлен'}\n\n"
        "<i>Эти данные используются для идентификации в системе</i>"
    )
    await message.answer(auth_text)

@router.message(Command("webapp"))
async def webapp_handler(message: types.Message):
    """Открывает веб-приложение"""
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text="🚀 Открыть веб-интерфейс",
        web_app=WebAppInfo(url=WEB_APP_URL)))
    await message.answer(
        "📲 Нажмите кнопку ниже для запуска веб-приложения:",
        reply_markup=builder.as_markup())

@router.callback_query(F.data == "subscribe")
async def subscribe(callback: CallbackQuery):
    """Обработчик подписки"""
    user_id = callback.from_user.id
    SUBSCRIPTIONS.add(user_id)
    await callback.answer(
        "✅ Вы успешно подписались на обновления!",
        show_alert=True)

@router.callback_query(F.data == "unsubscribe")
async def unsubscribe(callback: CallbackQuery):
    """Обработчик отписки"""
    user_id = callback.from_user.id
    SUBSCRIPTIONS.discard(user_id)
    await callback.answer(
        "❌ Вы отписались от рассылки уведомлений",
        show_alert=True)

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
