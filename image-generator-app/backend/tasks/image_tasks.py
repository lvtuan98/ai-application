from celery import Celery
from flask import current_app
from minio import Minio
from minio.error import S3Error
import requests
from io import BytesIO
import uuid
import os


app = Celery()

@app.task
def generate_image_task(data):
    try:
        response = requests.post(f"{current_app.config['AI_WORKER_URL']}/generate", json=data)
        image_data = response.content

        minio_client = Minio(
            current_app.config['MINIO_ENDPOINT'],
            access_key=current_app.config['MINIO_ACCESS_KEY'],
            secret_key=current_app.config['MINIO_SECRET_KEY'],
            secure=False
        )

        if not minio_client.bucket_exists(current_app.config['MINIO_BUCKET_NAME']):
            minio_client.make_bucket(current_app.config['MINIO_BUCKET_NAME'])

        image_id = str(uuid.uuid4())
        image_path = f"{image_id}.png"
        minio_client.put_object(
            current_app.config['MINIO_BUCKET_NAME'],
            image_path,
            BytesIO(image_data),
            length=len(image_data),
            content_type='image/png'
        )

        image_url = minio_client.presigned_get_object(current_app.config['MINIO_BUCKET_NAME'], image_path)
        return {"image_url": image_url}
    except S3Error as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": str(e)}
