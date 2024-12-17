FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE 1  # Отключаем создание .pyc файлов
ENV PYTHONUNBUFFERED 1  # Убеждаемся, что вывод логов сразу идет в консоль (без буферизации)

WORKDIR /app

RUN pip install --upgrade pip
COPY ../requirements/requirements.txt .
RUN pip install -r requirements.txt

COPY ../tests ./tests
COPY ../src ./src
ENTRYPOINT [ "/bin/sh", "-c", "pytest" ]