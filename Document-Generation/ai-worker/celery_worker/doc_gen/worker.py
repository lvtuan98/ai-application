import os

import django
from celery import Celery
from kombu import Queue

from celery_worker.doc_gen.client_connector import (
    BROKER_URL,
    CeleryConnector
)

app: Celery = Celery(
    "postman",
    broker=BROKER_URL,
    include=[
        "celery_worker.doc_gen.process_tasks",
    ],
)

app.conf.update(
    {
        "task_queues": [
            Queue("doc_gen"),
        ],
        "task_routes": CeleryConnector.task_routes
    }
)

if __name__ == "__main__":
    argv = ["worker", "--loglevel=INFO", "--pool=solo"]  # Window opts
    app.worker_main(argv)
