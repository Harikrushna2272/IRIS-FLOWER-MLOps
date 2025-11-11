FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim

WORKDIR /api

COPY . .

EXPOSE 8000

CMD ["uv", "run", "fastapi", "run", "main.py", "--port", "8000"]
