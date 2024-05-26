import json
import os
import uuid
from datetime import timedelta

from minio import Minio
from minio.error import S3Error
from dotenv import load_dotenv
load_dotenv()

BACKEND_SERVER = os.environ.get("BE_URL")
MINIO_HOST = os.environ.get("MINIO_HOST")
MINIO_PORT = os.environ.get("MINIO_PORT")
MINIO_ROOT_USER = os.environ.get("MINIO_ROOT_USER")
MINIO_ROOT_PASSWORD = os.environ.get("MINIO_ROOT_PASSWORD")
# ENDPOINT = f"{MINIO_HOST}:{MINIO_PORT}"
ENDPOINT = os.environ.get('MINIO_ENDPOINT')
BUCKET_NAME = os.environ.get("MINIO_BUCKET_NAME")

from enum import Enum


class ContentType(Enum):
    DOCX = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    PPTX = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    PDF = "application/pdf"
    JSON = "application/json"
    PNG = "image/png"
    JPEG = "image/jpeg"
    JPG = "image/jpg"


class MinIOClient:
    def __init__(
        self,
        endpoint: str,
        access_key: str,
        secret_key: str,
        bucket_name: str,
    ):
        self.client = Minio(
            endpoint=endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=False,
        )
        self.bucket_name = bucket_name
        self.create_bucket(bucket_name=self.bucket_name)

    def create_bucket(self, bucket_name):
        # print(bucket_name)
        found = self.client.bucket_exists(bucket_name)
        if not found:
            self.client.make_bucket(bucket_name)
            policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Sid": "",
                        "Effect": "Allow",
                        "Principal": {"AWS": "*"},
                        "Action": "s3:GetBucketLocation",
                        "Resource": f"arn:aws:s3:::{bucket_name}",
                    },
                    {
                        "Sid": "",
                        "Effect": "Allow",
                        "Principal": {"AWS": "*"},
                        "Action": "s3:ListBucket",
                        "Resource": f"arn:aws:s3:::{bucket_name}",
                    },
                    {
                        "Sid": "",
                        "Effect": "Allow",
                        "Principal": {"AWS": "*"},
                        "Action": "s3:GetObject",
                        "Resource": f"arn:aws:s3:::{bucket_name}/*",
                    },
                    {
                        "Sid": "",
                        "Effect": "Allow",
                        "Principal": {"AWS": "*"},
                        "Action": "s3:PutObject",
                        "Resource": f"arn:aws:s3:::{bucket_name}/*",
                    },
                ],
            }
            self.client.set_bucket_policy(bucket_name, json.dumps(policy))
        else:
            print(f"Bucket {bucket_name} already exists")

    def upload_file(self, object_name, data, extension):
        extension = extension.upper()
        result = self.client.put_object(
            bucket_name=self.bucket_name,
            object_name=object_name,
            data=data,
            length=-1,
            part_size=10 * 1024 * 1024,
            content_type=getattr(ContentType, extension).value,
        )

    def upload(self, object_name, file_path, extension):
        extension = extension.upper()
        result = self.client.fput_object(
            bucket_name=self.bucket_name,
            object_name=object_name,
            file_path=file_path,
            content_type=getattr(ContentType, extension).value,
        )
        return result.object_name

    def get_file(self, object_name, file_path):
        response = self.client.fget_object(
            bucket_name=self.bucket_name,
            object_name=object_name,
            file_path=file_path,
        )
        return response

    def get_object(self, object_name):
        return self.client.get_object(
            bucket_name=self.bucket_name, object_name=object_name
        )

    def delete_file(self, object_name):
        self.client.remove_object(
            bucket_name=self.bucket_name, object_name=object_name
        )

    def get_url(
        self,
        object_name,
        time_expires=timedelta(hours=1),
        response_headers=None,
    ):
        url = self.client.get_presigned_url(
            "GET",
            bucket_name=self.bucket_name,
            object_name=object_name,
            expires=time_expires,
            response_headers=response_headers,
        )
        be_host = str(BACKEND_SERVER).split("//")[-1].split(":")[0]
        return url.replace(ENDPOINT, f"{be_host}:{MINIO_PORT}").split("?")[0]

minio_client = MinIOClient(
    endpoint=ENDPOINT,
    access_key=MINIO_ROOT_USER,
    secret_key=MINIO_ROOT_PASSWORD,
    bucket_name=BUCKET_NAME,
)
