FROM python:3.13-slim

# Встановлення робочої директорії
WORKDIR /app

# Копіюємо файли
COPY . .

# Встановлення залежностей із requirements.txt
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Відкриваємо порт
EXPOSE 5000

# Запуск додатку
CMD ["python", "API.py"]