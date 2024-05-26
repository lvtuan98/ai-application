FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

ARG BE_HOST
ARG BE_PORT
ENV BE_HOST $BE_HOST
ENV BE_PORT $BE_PORT

CMD ["gunicorn", "--workers", "3", "--bind", "${BE_HOST}:${BE_PORT}", "backend.wsgi:application"]
