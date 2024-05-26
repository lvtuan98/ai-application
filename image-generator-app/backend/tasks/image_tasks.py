from celery import current_app as celery_app
from flask import current_app as flask_app
from minio import Minio
from minio.error import S3Error
import requests
from io import BytesIO
import uuid
import os
import base64
from datetime import timedelta

from services.minio_service import ContentType, minio_client

from dotenv import load_dotenv
load_dotenv()

@celery_app.task
def generate_image_task(data):
    try:
        response = requests.post(f"{os.environ.get('AI_WORKER_URL')}/generate", json=data)
        image_data = base64.b64decode(response.content)
        # print("image_data", image_data, flush=True)


        # minio_client = Minio(
        #     os.environ.get('MINIO_ENDPOINT'),
        #     access_key=os.environ.get('MINIO_ROOT_USER'),
        #     secret_key=os.environ.get('MINIO_ROOT_PASSWORD'),
        #     secure=False
        # )

        # if not minio_client.bucket_exists(os.environ.get('MINIO_BUCKET_NAME')):
        #     minio_client.make_bucket(os.environ.get('MINIO_BUCKET_NAME'))

        # image_id = str(uuid.uuid4())
        # image_path = f"{image_id}.png"
        # minio_client.put_object(
        #     os.environ.get('MINIO_BUCKET_NAME'),
        #     image_path,
        #     BytesIO(image_data),
        #     length=len(image_data),
        #     content_type='image/png'
        # )

        extension = "png"
        image_id = str(uuid.uuid4())
        file_name = f"{image_id}.{extension}"
        binary_img = BytesIO(image_data)
        minio_client.upload_file(
            object_name=file_name, data=binary_img, extension=extension
        )

        image_url = minio_client.get_url(
            object_name=file_name,
            time_expires=timedelta(hours=1),
            response_headers={
                "response-content-disposition": f"attachment; filename={file_name}",
                "response-content-type": getattr(
                    ContentType, extension.upper()
                ).value,
            },
        )
        return {"image_url": image_url}
    except S3Error as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": str(e)}
