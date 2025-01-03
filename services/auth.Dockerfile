FROM python:3.12-slim as base

ENV PYTHONDONTWRITEBYTECODE 1  # Отключаем создание .pyc файлов
ENV PYTHONUNBUFFERED 1  # Убеждаемся, что вывод логов сразу идет в консоль (без буферизации)
ENV VIRTUAL_ENV=/opt/venv

ENV PATH="${VIRTUAL_ENV}/bin:$PATH"

FROM base as builder
ENV POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_VERSION=1.8.5

COPY poetry.lock pyproject.toml ./
RUN python -m venv ${VIRTUAL_ENV}
RUN pip install --no-cache-dir poetry==$POETRY_VERSION
RUN poetry install --with auth --no-root --no-interaction --no-ansi

FROM base as runner
COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}
COPY services/auth /auth
WORKDIR /auth
RUN useradd -ms /bin/bash developer
USER developer
ENV PORT=8080
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT} --log-config=log_config.yml
