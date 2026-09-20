# ai.py
import os
from openai import OpenAI
from config import SYSTEM_PROMPT

# === НАСТРОЙКИ DEEPSEEK ===
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")
DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"
MODEL_NAME = "deepseek-chat"

client = OpenAI(base_url=DEEPSEEK_BASE_URL, api_key=DEEPSEEK_API_KEY)

# Храним историю диалогов (user_id -> list of messages)
chat_sessions = {}

def get_history(user_id: int) -> list:
    """Получить или создать историю для пользователя"""
    if user_id not in chat_sessions:
        chat_sessions[user_id] = []
    return chat_sessions[user_id]

def ask_ai(user_id: int, message: str) -> str:
    """Отправить сообщение в DeepSeek и получить ответ"""
    try:
        history = get_history(user_id)
        
        # Формируем сообщения: системный промпт + история + новое сообщение
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages.extend(history[-10:])  # последние 10 сообщений
        messages.append({"role": "user", "content": message})
        
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=0.7,
            max_tokens=500,
            timeout=30.0,
        )
        
        answer = response.choices[0].message.content
        
        # Обновляем историю
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