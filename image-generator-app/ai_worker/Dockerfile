FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

CMD ["gunicorn", "--workers", "3", "--bind", "0.0.0.0:5001", "ai_worker.wsgi:application"]
