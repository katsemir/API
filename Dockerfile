FROM python:3.13-slim

# Встановлення робочої директорії
WORKDIR /app

# Копіюємо файли
COPY . .

# Встановлення залежностей
RUN pip install --no-cache-dir flask flask-restful flask-sqlalchemy

# Відкриваємо порт
EXPOSE 5000

# Запуск додатку
CMD ["python", "API.py"]