FROM python:3.13-slim

WORKDIR /app

# Install uv and uvx
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY pyproject.toml uv.lock ./

RUN uv sync --locked --no-install-project

COPY . .

EXPOSE 8000
