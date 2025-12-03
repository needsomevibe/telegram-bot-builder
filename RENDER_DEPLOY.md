# Инструкция по деплою на Render

Это руководство поможет вам развернуть Telegram Bot Builder на Render.

## Предварительные требования

1. Аккаунт на [Render.com](https://render.com)
2. GitHub репозиторий с вашим кодом (или подключите Git репозиторий)
3. Telegram API credentials (получите на https://my.telegram.org/apps)

## Шаг 1: Подготовка переменных окружения

Перед деплоем вам нужно подготовить следующие переменные окружения:

### Обязательные переменные:
- `DATABASE_URL` - будет автоматически создана при создании PostgreSQL базы данных
- `SESSION_SECRET` - секретный ключ для сессий (можно сгенерировать случайную строку)
- `TELEGRAM_API_ID` - ваш Telegram API ID (получите на https://my.telegram.org/apps)
- `TELEGRAM_API_HASH` - ваш Telegram API Hash

### Опциональные переменные:
- `GITHUB_PERSONAL_ACCESS_TOKEN` - токен для синхронизации с GitHub
- `VITE_TELEGRAM_BOT_USERNAME` - username вашего бота (по умолчанию: `botcraft_studio_bot`)

## Шаг 2: Деплой через Render Dashboard

### Вариант A: Автоматический деплой через render.yaml (рекомендуется)

1. Зайдите на [Render Dashboard](https://dashboard.render.com)
2. Нажмите "New +" → "Blueprint"
3. Подключите ваш GitHub репозиторий
4. Render автоматически обнаружит `render.yaml` и создаст все необходимые сервисы

### Вариант B: Ручной деплой

#### 2.1. Создание PostgreSQL базы данных

1. В Render Dashboard нажмите "New +" → "PostgreSQL"
2. Выберите:
   - **Name**: `telegram-bot-builder-db`
   - **Database**: `telegram_bot_builder`
   - **User**: `telegram_bot_builder_user`
   - **Plan**: Free (или выберите нужный план)
3. Нажмите "Create Database"
4. После создания скопируйте **Internal Database URL** - это будет ваш `DATABASE_URL`

#### 2.2. Создание основного веб-сервиса

1. В Render Dashboard нажмите "New +" → "Web Service"
2. Подключите ваш GitHub репозиторий
3. Настройте сервис:
   - **Name**: `telegram-bot-builder`
   - **Environment**: `Node`
   - **Build Command**: `npm ci && npm run build`
   - **Start Command**: `npm start`
   - **Plan**: Free (или выберите нужный план)

4. Добавьте переменные окружения:
   - `NODE_ENV` = `production`
   - `PORT` = `5000`
   - `DATABASE_URL` = (скопируйте из созданной базы данных)
   - `SESSION_SECRET` = (сгенерируйте случайную строку, например через `openssl rand -hex 32`)
   - `TELEGRAM_API_ID` = (ваш API ID)
   - `TELEGRAM_API_HASH` = (ваш API Hash)
   - `GITHUB_PERSONAL_ACCESS_TOKEN` = (опционально)
   - `VITE_TELEGRAM_BOT_USERNAME` = (опционально)

5. Нажмите "Create Web Service"

#### 2.3. Создание Flask сервиса для keep-alive

1. В Render Dashboard нажмите "New +" → "Web Service"
2. Подключите тот же GitHub репозиторий
3. Настройте сервис:
   - **Name**: `telegram-bot-builder-keepalive`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python keepalive.py`
   - **Plan**: Free

4. Добавьте переменные окружения:
   - `TARGET_URL` = (URL вашего основного сервиса, например: `https://telegram-bot-builder.onrender.com`)
   - `PING_INTERVAL` = `300` (интервал пинга в секундах, 5 минут)

5. Нажмите "Create Web Service"

## Шаг 3: Применение миграций базы данных

После создания базы данных нужно применить миграции:

1. Зайдите в ваш основной веб-сервис на Render
2. Откройте вкладку "Shell"
3. Выполните команду:
   ```bash
   npm run db:push
   ```

Или используйте Drizzle Kit для применения миграций:
```bash
npx drizzle-kit push
```

## Шаг 4: Проверка работы

1. Дождитесь завершения деплоя всех сервисов
2. Откройте URL вашего основного сервиса (например: `https://telegram-bot-builder.onrender.com`)
3. Проверьте health check: `https://your-app.onrender.com/api/health`
4. Убедитесь, что Flask сервис keep-alive работает и пингует основной сервис

## Важные замечания

### О бесплатном плане Render

- **Free tier** сервисы засыпают после 15 минут неактивности
- Flask сервис keep-alive предотвращает засыпание, отправляя периодические запросы
- Первый запрос после засыпания может занять до 30 секунд (cold start)

### О производительности

- Для production использования рекомендуется использовать платные планы
- Настройте автоматические бэкапы базы данных
- Используйте CDN для статических файлов

### О безопасности

- Никогда не коммитьте `.env` файлы в репозиторий
- Используйте сильные секретные ключи для `SESSION_SECRET`
- Регулярно обновляйте зависимости

## Решение проблем

### Проблема: Сервис не запускается

**Решение:**
- Проверьте логи в Render Dashboard
- Убедитесь, что все переменные окружения установлены
- Проверьте, что `DATABASE_URL` корректна

### Проблема: База данных не подключается

**Решение:**
- Убедитесь, что используете **Internal Database URL** (не External)
- Проверьте, что база данных создана и запущена
- Примените миграции через Shell

### Проблема: Сервис засыпает

**Решение:**
- Убедитесь, что Flask keep-alive сервис работает
- Проверьте, что `TARGET_URL` в keep-alive сервисе указывает на правильный URL
- Уменьшите `PING_INTERVAL` до 180 секунд (3 минуты) для более частых пингов

### Проблема: Ошибки при сборке

**Решение:**
- Проверьте, что все зависимости указаны в `package.json`
- Убедитесь, что Node.js версия совместима (используется Node 20)
- Проверьте логи сборки в Render Dashboard

## Дополнительные ресурсы

- [Render Documentation](https://render.com/docs)
- [Drizzle ORM Documentation](https://orm.drizzle.team)
- [Telegram Bot API](https://core.telegram.org/bots/api)

## Поддержка

Если у вас возникли проблемы, проверьте:
1. Логи в Render Dashboard
2. Health check endpoint: `/api/health`
3. Статус всех сервисов в Render Dashboard

