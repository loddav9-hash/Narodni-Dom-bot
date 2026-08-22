# ai.py
import google.generativeai as genai
from config import GEMINI_API_KEY, SYSTEM_PROMPT

# Настройка Gemini
genai.configure(api_key=GEMINI_API_KEY)

# Модель
model = genai.GenerativeModel(
    model_name="gemini-3.6-flash",
    system_instruction=SYSTEM_PROMPT
    НЕ ИСПОЛЬЗУЙ Markdown-разметку (звёздочки, подчёркивания для форматирования). Пиши простым текстом.
)

# Храним историю диалогов (user_id -> list of messages)
chat_sessions = {}

def get_chat(user_id: int):
    """Получить или создать сессию чата для пользователя"""
    if user_id not in chat_sessions:
        chat_sessions[user_id] = model.start_chat(history=[])
    return chat_sessions[user_id]

def ask_ai(user_id: int, message: str) -> str:
    """Отправить сообщение в Gemini и получить ответ"""
    try:
        chat = get_chat(user_id)
        response = chat.send_message(message)
        return response.text
    except Exception as e:
        print(f"Error with Gemini: {e}")
        return "Извините, произошла ошибка. Попробуйте ещё раз через минуту."

def clear_chat(user_id: int):
    """Очистить историю диалога"""
    if user_id in chat_sessions:
        del chat_sessions[user_id]