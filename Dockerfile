# Используем официальный Node.js образ
FROM node:20-alpine AS builder

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем package.json и package-lock.json
COPY package*.json ./

# Устанавливаем все зависимости (включая devDependencies для сборки)
RUN npm install

# Копируем остальные файлы
COPY . .

# Собираем приложение
RUN npm run build

# Production образ
FROM node:20-alpine

WORKDIR /app

# Копируем package.json для production зависимостей
COPY package*.json ./

# Устанавливаем только production зависимости
RUN npm ci --only=production

# Копируем собранное приложение из builder
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/shared ./shared
COPY --from=builder /app/migrations ./migrations

# Создаем директорию для uploads
RUN mkdir -p uploads

# Открываем порт
EXPOSE 5000

# Запускаем приложение
CMD ["npm", "start"]

