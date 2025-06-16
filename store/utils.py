# store/utils.py
import os
import requests

def send_telegram_message(text: str) -> None:
    """
    Відправляє повідомлення в Telegram за допомогою Bot API.
    Потрібно задати через .env:
      TELEGRAM_TOKEN і TELEGRAM_CHAT_ID
    """
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    if not token or not chat_id:
        # Якщо не вказані змінні середовища — нічого не надсилати
        return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'HTML',
    }
    try:
        response = requests.post(url, json=payload, timeout=5)
        response.raise_for_status()
    except requests.RequestException:
        # Можна додати логування помилок, якщо потрібно
        pass
