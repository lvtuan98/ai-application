import os

class Config:
    DEBUG = True
    AI_WORKER_URL = 'http://ai-worker:5001'
    CELERY_BROKER_URL = 'redis://redis:6379/0'
    CELERY_RESULT_BACKEND = 'redis://redis:6379/0'
    MINIO_ENDPOINT = 'minio:9000'
    MINIO_ACCESS_KEY = os.getenv('MINIO_ACCESS_KEY', 'minio')
    MINIO_SECRET_KEY = os.getenv('MINIO_SECRET_KEY', 'minio123')
    MINIO_BUCKET_NAME = 'images'
