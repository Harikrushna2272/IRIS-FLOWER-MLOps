FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim

WORKDIR /app
COPY . .

EXPOSE 8001

CMD ["uv", "run", "fastapi", "run", "main.py", "--port", "8001", "--host", "0.0.0.0"]
