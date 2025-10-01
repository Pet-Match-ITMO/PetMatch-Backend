FROM python:3.12-slim-bookworm

RUN pip install uv==0.6.6

WORKDIR /app

ENV PYTHONPATH=/app

COPY ./pyproject.toml .
COPY uv.lock .

RUN uv sync 

COPY app /app
COPY alembic.ini .
COPY .python-version .
COPY main.py .

EXPOSE 8080

CMD ["uv","run","main.py"]