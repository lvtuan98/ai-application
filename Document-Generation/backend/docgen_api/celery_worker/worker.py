import os

import django
from celery import Celery
from kombu import Queue
from docgen import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "docgen.settings")
django.setup()

app: Celery = Celery(
    "postman",
    broker=settings.BROKER_URL,
    include=[
        "docgen_api.celery_worker.process_result_tasks",
    ],
)

app.conf.update(
    {
        "task_queues": [
            Queue("doc_gen_rs"),
        ],
        "task_routes": {
            "process_doc_gen_result": {"queue": "doc_gen_rs"},
        },
    }
)

if __name__ == "__main__":
    argv = ["worker", "--loglevel=INFO", "--pool=solo"]  # Window opts
    app.worker_main(argv)
