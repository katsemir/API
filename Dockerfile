# Використовуємо офіційний образ Python
FROM python:3.10

# Встановлюємо робочу директорію
WORKDIR /app

# Копіюємо всі файли проєкту в контейнер
COPY . .

# Встановлюємо бібліотеки
RUN pip install --no-cache-dir -r requirements.txt

# Відкриваємо порт 5000 для Flask
EXPOSE 5000

# Запускаємо API
CMD ["python", "API.py"]