FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

ARG AI_WORKER_HOST
ARG AI_WORKER_PORT
ENV AI_WORKER_HOST $AI_WORKER_HOST
ENV AI_WORKER_PORT $AI_WORKER_PORT

CMD ["gunicorn", "--workers", "3", "--bind", "${AI_WORKER_HOST}:${AI_WORKER_PORT}", "ai_worker.wsgi:application"]
