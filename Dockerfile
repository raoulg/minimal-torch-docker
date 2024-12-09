FROM python:3.11-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
WORKDIR /app
RUN uv pip install --system torch numpy --index-url https://download.pytorch.org/whl/cpu
