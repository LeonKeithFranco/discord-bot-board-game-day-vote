# deps
FROM ghcr.io/astral-sh/uv:python3.14-bookworm-slim AS deps

ENV UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_DOWNLOADS=0

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv sync --locked --no-dev


# source
FROM scratch AS source

WORKDIR /app

COPY main.py .
COPY src ./src


# runtime
FROM python:3.14-slim-bookworm AS runtime

RUN groupadd --system app && \
    useradd --system --gid app --create-home app

WORKDIR /app

COPY --from=deps --chown=app:app /app/.venv ./.venv
COPY --from=source --chown=app:app /app .

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1

USER app

CMD ["python", "main.py"]
