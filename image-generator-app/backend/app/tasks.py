from celery import shared_task
from minio import Minio
from minio.error import S3Error
import requests
from io import BytesIO
import uuid
import os

@shared_task
def generate_image_task(data):
    try:
        response = requests.post(f"http://ai-worker:5001/generate", json=data)
        image_data = response.content

        minio_client = Minio(
            os.getenv('MINIO_ENDPOINT', 'minio:9000'),
            access_key=os.getenv('MINIO_ACCESS_KEY', 'minio'),
            secret_key=os.getenv('MINIO_SECRET_KEY', 'minio123'),
            secure=False
        )

        bucket_name = os.getenv('MINIO_BUCKET_NAME', 'images')
        if not minio_client.bucket_exists(bucket_name):
            minio_client.make_bucket(bucket_name)

        image_id = str(uuid.uuid4())
        image_path = f"{image_id}.png"
        minio_client.put_object(
            bucket_name,
            image_path,
            BytesIO(image_data),
            length=len(image_data),
            content_type='image/png'
        )

        image_url = minio_client.presigned_get_object(bucket_name, image_path)
        return {"image_url": image_url}
    except S3Error as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": str(e)}
