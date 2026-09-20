# ai.py
import os
from openai import OpenAI
from config import SYSTEM_PROMPT
from database import get_available_beds, get_available_private

# === НАСТРОЙКИ DEEPSEEK ===
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")
DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"
MODEL_NAME = "deepseek-chat"

client = OpenAI(base_url=DEEPSEEK_BASE_URL, api_key=DEEPSEEK_API_KEY)

# Храним историю диалогов (user_id -> list of messages)
chat_sessions = {}

def get_availability_context(check_in: str = None, check_out: str = None) -> str:
    """
    Формирует строку с информацией о свободных местах.
    Если даты не указаны — возвращает общую информацию.
    """
    if check_in and check_out:
        beds = get_available_beds(check_in, check_out)
        rooms = get_available_private(check_in, check_out)
        return f"На даты {check_in} — {check_out}: свободно {beds} мест в дорме, {rooms} приватных комнат."
    else:
        return "Всего в хостеле: 8 мест в дорме, 2 приватные комнаты."

def get_history(user_id: int) -> list:
    """Получить или создать историю для пользователя"""
    if user_id not in chat_sessions:
        chat_sessions[user_id] = []
    return chat_sessions[user_id]

def ask_ai(user_id: int, message: str) -> str:
    """Отправить сообщение в DeepSeek и получить ответ"""
    try:
        history = get_history(user_id)
        
        # Получаем информацию о свободных местах
        availability = get_availability_context()
        
        # Формируем системный промпт с актуальной информацией
        system_prompt = SYSTEM_PROMPT + "\n\nАКТУАЛЬНАЯ ИНФОРМАЦИЯ:\n" + availability
        
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(history[-10:])
        messages.append({"role": "user", "content": message})
        
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=0.7,
            max_tokens=500,
            timeout=30.0,
        )
        
        answer = response.choices[0].message.content
        
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": answer})
        chat_sessions[user_id] = history[-10:]
        
        return answer
    except Exception as e:
        import traceback
        print("=== ОШИБКА ИИ ===")
        traceback.print_exc()
        print("=================")
        return "Извините, произошла ошибка. Попробуйте ещё раз через минуту."

def clear_chat(user_id: int):
    """Очистить историю диалога"""
    if user_id in chat_sessions:
        del chat_sessions[user_id]