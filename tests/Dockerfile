FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE 1  # Отключаем создание .pyc файлов
ENV PYTHONUNBUFFERED 1  # Убеждаемся, что вывод логов сразу идет в консоль (без буферизации)

WORKDIR /app

COPY ../tests ./tests
RUN pip install --upgrade pip
RUN cd ./tests && pip install -r requirements.txt

COPY ../project ./project
COPY ../pyproject.toml ./pyproject.toml



ENTRYPOINT [ "/bin/sh", "-c", "pytest" ]