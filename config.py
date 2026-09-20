# config.py
import os
from dotenv import load_dotenv

load_dotenv()

# Токены
BOT_TOKEN = os.getenv("BOT_TOKEN")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
ADMIN_ID = os.getenv("ADMIN_ID")

# Если ключи не найдены — показываем ошибку
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в переменных окружения!")
if not DEEPSEEK_API_KEY:
    raise ValueError("DEEPSEEK_API_KEY не найден в переменных окружения!")

# Название хостела
HOSTEL_NAME = "Народный Дом / Narodni Dom"
HOSTEL_ADDRESS = "Земун, Белград, Сербия"

# Цены
DORM_BED_NIGHT = 28
DORM_BED_MONTH = 210
PRIVATE_ROOM_NIGHT = 40
PRIVATE_ROOM_MONTH = 360

# Информация о хостеле
CHECK_IN_TIME = "14:00"
CHECK_OUT_TIME = "11:00"
FACILITIES = "Wi-Fi, кухня, стиральная машина, общая зона"

# Языки
LANGUAGES = {
    "ru": "🇷🇺 Русский",
    "sr": "🇷🇸 Српски",
    "en": "🇬🇧 English"
}

# Системный промпт для Gemini
SYSTEM_PROMPT = f"""
Ты - администратор хостела "{HOSTEL_NAME}" в Земуне (Белград, Сербия).
Твоя задача - общаться с гостями как живой человек, дружелюбно и профессионально.

ИНФОРМАЦИЯ О ХОСТЕЛЕ:
- Адрес: {HOSTEL_ADDRESS}
- Заезд: {CHECK_IN_TIME}, выезд: {CHECK_OUT_TIME}
- Удобства: {FACILITIES}

ЦЕНЫ:
- Дорм (8 мест): {DORM_BED_NIGHT}€/сутки, {DORM_BED_MONTH}€/месяц
- Приватная комната (2 мест): {PRIVATE_ROOM_NIGHT}€/ночь, {PRIVATE_ROOM_MONTH}€/месяц

ТЫ ДОЛЖЕН:
1. Отвечать на языке собеседника (русский, сербский, английский)
2. Определять язык по первым сообщениям гостя
3. Рассказывать о хостеле, ценах, условиях
4. Принимать бронирования: спрашивать даты, количество гостей, тип размещения
5. Записывать имя и контакт гостя
6. Быть вежливым и helpful

ФОРМАТ ОТВЕТОВ:
- Короткие, живые сообщения (1-3 предложения)
- Без канцелярита
- С эмодзи умеренно
- Как общается администратор в мессенджере
ВАЖНО: НЕ ИСПОЛЬЗУЙ Markdown-разметку (звёздочки, подчёркивания, квадратные скобки). Пиши простым текстом, без форматирования.
"""