# keep_alive.py
from flask import Flask
from threading import Thread
import requests
import time
import logging

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    """Запускает веб-сервер и пингует сам себя"""
    t = Thread(target=run)
    t.start()
    
    # Пинг каждые 5 минут для предотвращения засыпания
    def ping_self():
        while True:
            try:
                # Пингуем свой же сервер
                requests.get("https://your-app.onrender.com", timeout=10)
                logging.info("Ping successful")
            except Exception as e:
                logging.error(f"Ping failed: {e}")
            time.sleep(300)  # 5 минут
    
    ping_thread = Thread(target=ping_self)
    ping_thread.start()