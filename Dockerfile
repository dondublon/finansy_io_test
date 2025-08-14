# Используем официальный образ Python
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем requirements и устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходники
COPY src/ ./src/

# Устанавливаем переменную окружения для модуля FastAPI
ENV PYTHONPATH=/app/src

# Открываем порт
EXPOSE 8000

# Запуск Uvicorn
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
