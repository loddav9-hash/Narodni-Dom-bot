# bot.py
import asyncio
import logging
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN, ADMIN_ID, HOSTEL_NAME, LANGUAGES
from database import init_db, save_booking, get_user_language, set_user_language, get_all_bookings
from ai import ask_ai, clear_chat

# Логирование
logging.basicConfig(level=logging.INFO)

# Инициализация бота
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Состояния для бронирования
class BookingStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_phone = State()
    waiting_for_dates = State()
    waiting_for_guests = State()
    waiting_for_room_type = State()
    waiting_for_confirmation = State()

# Клавиатура главного меню
def get_main_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 О хостеле", callback_data="about")],
        [InlineKeyboardButton(text="💰 Цены", callback_data="prices")],
        [InlineKeyboardButton(text="📅 Забронировать", callback_data="book")],
        [InlineKeyboardButton(text="🛏 Свободные места", callback_data="availability")],
        [InlineKeyboardButton(text="📞 Контакты", callback_data="contacts")],
        [InlineKeyboardButton(text="🌍 Language / Jezik", callback_data="language")]
    ])
    return keyboard

# Старт
@dp.message(Command("start"))
async def cmd_start(message: Message):
    user_id = message.from_user.id
    clear_chat(user_id)
    
    welcome_text = (
        f"👋 Добро пожаловать в {HOSTEL_NAME}!\n"
        f"Я администратор хостела. Отвечу на все вопросы и помогу с бронью.\n\n"
        f"🇷🇸 Dobrodošli u {HOSTEL_NAME}!\n"
        f"Ja sam administrator hostela. Odgovaram na sva pitanja i pomažem sa rezervacijom.\n\n"
        f"🇬🇧 Welcome to {HOSTEL_NAME}!\n"
        f"I'm the hostel administrator. I'll answer all questions and help with booking."
    )
    
    await message.answer(welcome_text, reply_markup=get_main_keyboard())

# Кнопка "О хостеле"
@dp.callback_query(F.data == "about")
async def about_hostel(callback: types.CallbackQuery):
    lang = get_user_language(callback.from_user.id)
    
    texts = {
        'ru': (
            f"🏠 *{HOSTEL_NAME}*\n\n"
            f"📍 {HOSTEL_NAME} находится в Земуне — самом атмосферном районе Белграда.\n\n"
            f"✨ У нас есть:\n"
            f"• Дорм на 8 мест\n"
            f"• Приватная комната на 2 гостей\n"
            f"• Wi-Fi\n"
            f"• Кухня\n"
            f"• Стиральная машина\n"
            f"• Уютная общая зона\n\n"
            f"🕐 Заезд: 14:00\n"
            f"🕐 Выезд: 11:00"
        ),
        'sr': (
            f"🏠 *{HOSTEL_NAME}*\n\n"
            f"📍 Nalazimo se u Zemunu — najatmosferskijem delu Beograda.\n\n"
            f"✨ Imamo:\n"
            f"• Dorm sa 8 kreveta\n"
            f"• Privatna soba za 2 gosta\n"
            f"• Wi-Fi\n"
            f"• Kuhinju\n"
            f"• Veš mašinu\n"
            f"• Udoban zajednički prostor\n\n"
            f"🕐 Prijava: 14:00\n"
            f"🕐 Odjava: 11:00"
        ),
        'en': (
            f"🏠 *{HOSTEL_NAME}*\n\n"
            f"📍 Located in Zemun — the most atmospheric district of Belgrade.\n\n"
            f"✨ We have:\n"
            f"• 8-bed dorm\n"
            f"• Private room for 2 guests\n"
            f"• Wi-Fi\n"
            f"• Kitchen\n"
            f"• Washing machine\n"
            f"• Cozy common area\n\n"
            f"🕐 Check-in: 14:00\n"
            f"🕐 Check-out: 11:00"
        )
    }
    
    await callback.message.answer(texts.get(lang, texts['ru']), parse_mode="Markdown")
    await callback.answer()

# Кнопка "Цены"
@dp.callback_query(F.data == "prices")
async def show_prices(callback: types.CallbackQuery):
    lang = get_user_language(callback.from_user.id)
    
    texts = {
        'ru': (
            f"💰 *Наши цены:*\n\n"
            f"🛏 *Дорм (8 мест):*\n"
            f"• 28€ / сутки\n"
            f"• 210€ / месяц\n\n"
            f"🚪 *Приватная комната (2 гостя):*\n"
            f"• 40€ / ночь\n"
            f"• 360€ / месяц\n\n"
            f"*Всё включено: Wi-Fi, кухня, стиральная машина*"
        ),
        'sr': (
            f"💰 *Naše cene:*\n\n"
            f"🛏 *Dorm (8 kreveta):*\n"
            f"• 28€ / dan\n"
            f"• 210€ / mesec\n\n"
            f"🚪 *Privatna soba (2 gosta):*\n"
            f"• 40€ / noć\n"
            f"• 360€ / mesec\n\n"
            f"*Sve uključeno: Wi-Fi, kuhinja, veš mašina*"
        ),
        'en': (
            f"💰 *Our prices:*\n\n"
            f"🛏 *Dorm (8 beds):*\n"
            f"• 28€ / night\n"
            f"• 210€ / month\n\n"
            f"🚪 *Private room (2 guests):*\n"
            f"• 40€ / night\n"
            f"• 360€ / month\n\n"
            f"*All included: Wi-Fi, kitchen, washing machine*"
        )
    }
    
    await callback.message.answer(texts.get(lang, texts['ru']), parse_mode="Markdown")
    await callback.answer()

# Кнопка "Контакты"
@dp.callback_query(F.data == "contacts")
async def show_contacts(callback: types.CallbackQuery):
    lang = get_user_language(callback.from_user.id)
    
    texts = {
        'ru': (
            f"📞 *Контакты {HOSTEL_NAME}:*\n\n"
            f"📍 Земун, Белград, Сербия\n"
            f"📱 Telegram: @NarodniDom_bot\n"
            f"🕐 На связи 24/7\n\n"
            f"Пишите в любое время — отвечу сразу!"
        ),
        'sr': (
            f"📞 *Kontakt {HOSTEL_NAME}:*\n\n"
            f"📍 Zemun, Beograd, Srbija\n"
            f"📱 Telegram: @NarodniDom_bot\n"
            f"🕐 Dostupni 24/7\n\n"
            f"Pišite u bilo koje vreme — odgovaram odmah!"
        ),
        'en': (
            f"📞 *Contacts {HOSTEL_NAME}:*\n\n"
            f"📍 Zemun, Belgrade, Serbia\n"
            f"📱 Telegram: @NarodniDom_bot\n"
            f"🕐 Available 24/7\n\n"
            f"Write anytime — I'll respond immediately!"
        )
    }
    
    await callback.message.answer(texts.get(lang, texts['ru']), parse_mode="Markdown")
    await callback.answer()

# Кнопка "Свободные места"
@dp.callback_query(F.data == "availability")
async def check_availability(callback: types.CallbackQuery):
    lang = get_user_language(callback.from_user.id)
    
    # Для MVP просто показываем статичную информацию
    texts = {
        'ru': (
            f"🛏 *Свободные места на ближайшие дни:*\n\n"
            f"• Дорм (8 мест): 5 свободных\n"
            f"• Приватная комната: занята до 25 числа\n\n"
            f"📅 Для точной проверки на ваши даты — напишите даты заезда и выезда, я проверю!"
        ),
        'sr': (
            f"🛏 *Slobodna mesta za naredne dane:*\n\n"
            f"• Dorm (8 kreveta): 5 slobodnih\n"
            f"• Privatna soba: zauzeta do 25.\n\n"
            f"📅 Za tačnu proveru za vaše datume — napišite datume dolaska i odlaska!"
        ),
        'en': (
            f"🛏 *Available beds for the coming days:*\n\n"
            f"• Dorm (8 beds): 5 available\n"
            f"• Private room: booked until the 25th\n\n"
            f"📅 For exact availability on your dates — tell me your check-in and check-out dates!"
        )
    }
    
    await callback.message.answer(texts.get(lang, texts['ru']), parse_mode="Markdown")
    await callback.answer()

# Кнопка "Забронировать"
@dp.callback_query(F.data == "book")
async def start_booking(callback: types.CallbackQuery, state: FSMContext):
    lang = get_user_language(callback.from_user.id)
    
    texts = {
        'ru': "Давайте забронируем! 🎉\n\nНапишите ваше имя:",
        'sr': "Hajde da rezervišemo! 🎉\n\nNapišite vaše ime:",
        'en': "Let's book! 🎉\n\nPlease write your name:"
    }
    
    await callback.message.answer(texts.get(lang, texts['ru']))
    await state.set_state(BookingStates.waiting_for_name)
    await callback.answer()

# Обработка имени
@dp.message(BookingStates.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    lang = get_user_language(message.from_user.id)
    
    texts = {
        'ru': "Отлично! Теперь напишите ваш номер телефона или Telegram для связи:",
        'sr': "Odlično! Sada napišite vaš broj telefona ili Telegram za kontakt:",
        'en': "Great! Now write your phone number or Telegram for contact:"
    }
    
    await message.answer(texts.get(lang, texts['ru']))
    await state.set_state(BookingStates.waiting_for_phone)

# Обработка телефона
@dp.message(BookingStates.waiting_for_phone)
async def process_phone(message: Message, state: FSMContext):
    await state.update_data(phone=message.text)
    lang = get_user_language(message.from_user.id)
    
    texts = {
        'ru': "Спасибо! Теперь укажите даты (например: с 25 октября по 30 октября):",
        'sr': "Hvala! Sada navedite datume (na primer: od 25. oktobra do 30. oktobra):",
        'en': "Thank you! Now specify the dates (for example: from October 25 to October 30):"
    }
    
    await message.answer(texts.get(lang, texts['ru']))
    await state.set_state(BookingStates.waiting_for_dates)

# Обработка дат
@dp.message(BookingStates.waiting_for_dates)
async def process_dates(message: Message, state: FSMContext):
    await state.update_data(dates=message.text)
    lang = get_user_language(message.from_user.id)
    
    texts = {
        'ru': "Сколько вас будет гостей?",
        'sr': "Koliko će vas biti gostiju?",
        'en': "How many guests will there be?"
    }
    
    await message.answer(texts.get(lang, texts['ru']))
    await state.set_state(BookingStates.waiting_for_guests)

# Обработка количества гостей
@dp.message(BookingStates.waiting_for_guests)
async def process_guests(message: Message, state: FSMContext):
    await state.update_data(guests=message.text)
    lang = get_user_language(message.from_user.id)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛏 Дорм (28€/сутки)", callback_data="room_dorm")],
        [InlineKeyboardButton(text="🚪 Приватная (40€/ночь)", callback_data="room_private")]
    ])
    
    texts = {
        'ru': "Какой тип размещения вас интересует?",
        'sr': "Koji tip smeštaja vas interesuje?",
        'en': "What type of accommodation are you interested in?"
    }
    
    await message.answer(texts.get(lang, texts['ru']), reply_markup=keyboard)
    await state.set_state(BookingStates.waiting_for_room_type)

# Обработка типа комнаты
@dp.callback_query(BookingStates.waiting_for_room_type)
async def process_room_type(callback: types.CallbackQuery, state: FSMContext):
    room_type = "Дорм (8 мест)" if callback.data == "room_dorm" else "Приватная комната (2 мест)"
    await state.update_data(room_type=room_type)
    
    data = await state.get_data()
    lang = get_user_language(callback.from_user.id)
    
    # Формируем сводку
    summary_texts = {
        'ru': (
            f"📋 *Проверьте детали бронирования:*\n\n"
            f"👤 Имя: {data.get('full_name')}\n"
            f"📞 Контакт: {data.get('phone')}\n"
            f"📅 Даты: {data.get('dates')}\n"
            f"👥 Гостей: {data.get('guests')}\n"
            f"🛏 Тип: {room_type}\n\n"
            f"Всё верно?"
        ),
        'sr': (
            f"📋 *Proverite detalje rezervacije:*\n\n"
            f"👤 Ime: {data.get('full_name')}\n"
            f"📞 Kontakt: {data.get('phone')}\n"
            f"📅 Datumi: {data.get('dates')}\n"
            f"👥 Gostiju: {data.get('guests')}\n"
            f"🛏 Tip: {room_type}\n\n"
            f"Sve tačno?"
        ),
        'en': (
            f"📋 *Check booking details:*\n\n"
            f"👤 Name: {data.get('full_name')}\n"
            f"📞 Contact: {data.get('phone')}\n"
            f"📅 Dates: {data.get('dates')}\n"
            f"👥 Guests: {data.get('guests')}\n"
            f"🛏 Type: {room_type}\n\n"
            f"All correct?"
        )
    }
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_booking"),
            InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_booking")
        ]
    ])
    
    await callback.message.answer(summary_texts.get(lang, summary_texts['ru']), parse_mode="Markdown", reply_markup=keyboard)
    await state.set_state(BookingStates.waiting_for_confirmation)
    await callback.answer()

# Подтверждение брони
@dp.callback_query(F.data == "confirm_booking", BookingStates.waiting_for_confirmation)
async def confirm_booking(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = get_user_language(callback.from_user.id)
    
    # Сохраняем бронь в БД
    booking_id = save_booking({
        'user_id': callback.from_user.id,
        'username': callback.from_user.username,
        'full_name': data.get('full_name'),
        'phone': data.get('phone'),
        'language': lang,
        'room_type': data.get('room_type'),
        'check_in': data.get('dates'),
        'check_out': data.get('dates'),
        'guests': data.get('guests'),
        'total_price': 0  # Потом можно считать
    })
    
    # Отправляем админу
    admin_text = (
        f"🔔 *Новая бронь #{booking_id}*\n\n"
        f"👤 {data.get('full_name')}\n"
        f"📞 {data.get('phone')} (@{callback.from_user.username})\n"
        f"📅 {data.get('dates')}\n"
        f"👥 {data.get('guests')} гостей\n"
        f"🛏 {data.get('room_type')}\n"
        f"🌍 Язык: {lang}"
    )
    
    try:
        await bot.send_message(ADMIN_ID, admin_text, parse_mode="Markdown")
    except Exception as e:
        print(f"Error sending to admin: {e}")
    
    success_texts = {
        'ru': (
            f"✅ *Бронь #{booking_id} подтверждена!*\n\n"
            f"Спасибо, {data.get('full_name')}!\n"
            f"Мы ждём вас в {HOSTEL_NAME}!\n\n"
            f"Если будут вопросы — пишите, я на связи 24/7 😊"
        ),
        'sr': (
            f"✅ *Rezervacija #{booking_id} potvrđena!*\n\n"
            f"Hvala, {data.get('full_name')}!\n"
            f"Čekamo vas u {HOSTEL_NAME}!\n\n"
            f"Ako imate pitanja — pišite, dostupan sam 24/7 😊"
        ),
        'en': (
            f"✅ *Booking #{booking_id} confirmed!*\n\n"
            f"Thank you, {data.get('full_name')}!\n"
            f"We're waiting for you at {HOSTEL_NAME}!\n\n"
            f"If you have questions — just write, I'm available 24/7 😊"
        )
    }
    
    await callback.message.answer(success_texts.get(lang, success_texts['ru']), parse_mode="Markdown")
    await state.clear()
    await callback.answer()

# Отмена брони
@dp.callback_query(F.data == "cancel_booking", BookingStates.waiting_for_confirmation)
async def cancel_booking(callback: types.CallbackQuery, state: FSMContext):
    lang = get_user_language(callback.from_user.id)
    
    texts = {
        'ru': "Бронирование отменено. Если передумаете — пишите! 😊",
        'sr': "Rezervacija otkazana. Ako se predomislite — pišite! 😊",
        'en': "Booking cancelled. If you change your mind — just write! 😊"
    }
    
    await callback.message.answer(texts.get(lang, texts['ru']))
    await state.clear()
    await callback.answer()

# Выбор языка
@dp.callback_query(F.data == "language")
async def choose_language(callback: types.CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru")],
        [InlineKeyboardButton(text="🇷🇸 Српски", callback_data="lang_sr")],
        [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")]
    ])
    await callback.message.answer("Выберите язык / Izaberite jezik / Choose language:", reply_markup=keyboard)
    await callback.answer()

# Обработка выбора языка
@dp.callback_query(F.data.startswith("lang_"))
async def set_language(callback: types.CallbackQuery):
    lang = callback.data.split("_")[1]
    set_user_language(callback.from_user.id, lang)
    
    confirmations = {
        'ru': "✅ Язык установлен: Русский",
        'sr': "✅ Jezik postavljen: Srpski",
        'en': "✅ Language set: English"
    }
    
    await callback.message.answer(confirmations.get(lang, confirmations['ru']))
    await callback.answer()

# Обработка всех остальных сообщений (через Gemini)
@dp.message()
async def handle_message(message: Message):
    user_id = message.from_user.id
    lang = get_user_language(user_id)
    
    # Показываем "печатает..."
    await bot.send_chat_action(message.chat.id, "typing")
    
    # Получаем ответ от ИИ
    ai_response = ask_ai(user_id, message.text)
    
    # Отправляем ответ
    await message.answer(ai_response)

# Команда для админа: посмотреть все брони
@dp.message(Command("bookings"))
async def show_bookings(message: Message):
    if str(message.from_user.id) != str(ADMIN_ID):
        await message.answer("⛔ У вас нет доступа к этой команде")
        return
    
    bookings = get_all_bookings()
    
    if not bookings:
        await message.answer("📭 Броней пока нет")
        return
    
    text = "📋 *Все брони:*\n\n"
    for b in bookings[:10]:  # Последние 10
        text += f"#{b[0]} | {b[3]} | {b[4]} | {b[6]} | {b[7]} | {b[8]} гостей | {b[10]}\n"
    
    await message.answer(text, parse_mode="Markdown")

# Запуск бота
async def main():
    init_db()
    print("✅ База данных инициализирована")
    print("🤖 Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())