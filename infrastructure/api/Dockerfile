FROM python:3.12-slim as builder

ENV PYTHONDONTWRITEBYTECODE 1  # Отключаем создание .pyc файлов
ENV PYTHONUNBUFFERED 1  # Убеждаемся, что вывод логов сразу идет в консоль (без буферизации)

RUN pip install --upgrade pip
COPY infrastructure/api/requirements.txt .
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install -r requirements.txt

FROM python:3.12-slim
COPY --from=builder /opt/venv /opt/venv
COPY services/api /api
WORKDIR /api
RUN useradd -ms /bin/bash developer
USER developer
ENV PATH="/opt/venv/bin:$PATH"
ENV PORT=8080
CMD uvicorn application.app:app --host 0.0.0.0 --port ${PORT}