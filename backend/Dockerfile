FROM python:3.12-slim

WORKDIR /app

RUN pip install uv

COPY pyproject.toml /app/pyproject.toml

RUN uv sync

COPY . /app

CMD ["uv", "run", "main.py"]