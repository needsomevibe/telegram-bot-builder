#!/usr/bin/env python3
"""
Flask сервис для поддержания активности основного приложения на Render.
Отправляет периодические запросы к основному сервису, чтобы он не засыпал.
"""

import os
import time
import requests
from flask import Flask, jsonify
from threading import Thread

app = Flask(__name__)

# URL основного приложения
TARGET_URL = os.getenv('TARGET_URL', 'http://localhost:5000')
# Интервал пинга в секундах (по умолчанию 5 минут)
PING_INTERVAL = int(os.getenv('PING_INTERVAL', '300'))

def ping_target():
    """Периодически отправляет запросы к основному приложению"""
    while True:
        try:
            # Пингуем health check endpoint
            health_url = f"{TARGET_URL}/api/health"
            response = requests.get(health_url, timeout=10)
            if response.status_code == 200:
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Ping successful: {response.status_code}")
            else:
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Ping failed: {response.status_code}")
        except Exception as e:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Ping error: {str(e)}")
        
        time.sleep(PING_INTERVAL)

@app.route('/')
def index():
    """Главная страница keep-alive сервиса"""
    return jsonify({
        'service': 'telegram-bot-builder-keepalive',
        'status': 'running',
        'target_url': TARGET_URL,
        'ping_interval': PING_INTERVAL
    })

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    # Запускаем поток для пинга в фоне
    ping_thread = Thread(target=ping_target, daemon=True)
    ping_thread.start()
    
    # Запускаем Flask сервер
    # Render автоматически устанавливает PORT, используем его или дефолтный 5001
    port = int(os.getenv('PORT', 5001))
    print(f"Starting keep-alive service on port {port}")
    print(f"Target URL: {TARGET_URL}")
    print(f"Ping interval: {PING_INTERVAL} seconds")
    app.run(host='0.0.0.0', port=port)

