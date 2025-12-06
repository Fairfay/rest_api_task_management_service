FROM python:3.12.3-slim

ARG SAFETY_API_KEY=${SAFETY_API_KEY}
ARG DJANGO_ENV=${DJANGO_ENV}

ENV DJANGO_ENV=${DJANGO_ENV} \
    SAFETY_API_KEY=${SAFETY_API_KEY} \
    PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=2.2.1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR='/var/cache/pypoetry' \
    POETRY_HOME='/usr/local'

SHELL ["/bin/bash", "-eo", "pipefail", "-c"]

RUN apt-get update && apt-get install -y --no-install-recommends \
    bash \
    build-essential \
    curl \
    gettext \
    git \
    libpq-dev \
    ca-certificates \
    gnupg \
 && curl -fsSL https://www.postgresql.org/media/keys/ACCC4CF8.asc \
    | gpg --dearmor -o /usr/share/keyrings/postgres.gpg \
 && echo "deb [signed-by=/usr/share/keyrings/postgres.gpg] \
    http://apt.postgresql.org/pub/repos/apt bookworm-pgdg main" \
    > /etc/apt/sources.list.d/pgdg.list \
 && apt-get update \
 && apt-get install -y postgresql-client-16 \
 && rm -rf /var/lib/apt/lists/*

# --------------------
# Установка Poetry через pip, curl запрос не доступен из РФ
# --------------------
RUN pip install --no-cache-dir "poetry==$POETRY_VERSION" \
 && poetry --version

WORKDIR /code

COPY pyproject.toml poetry.lock ./

RUN poetry install

COPY . .

RUN chmod +x start.sh

RUN if [ -n "${SAFETY_API_KEY}" ]; then \
        echo "Running safety scan..."; \
        poetry run safety --stage production --key "${SAFETY_API_KEY}" scan; \
        SCAN_EXIT_CODE=$?; \
        if [ $SCAN_EXIT_CODE -ne 0 ]; then \
            echo "Vulnerabilities found, failing build"; \
            exit $SCAN_EXIT_CODE; \
        fi; \
    else \
        echo "Skipping safety scan (no API key provided)"; \
    fi
