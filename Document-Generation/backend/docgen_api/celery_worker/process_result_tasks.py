import io
import sys
import logging
import base64
from celery.utils.log import get_task_logger
from rest_framework.response import Response
from rest_framework import status
from django.core.files.uploadedfile import TemporaryUploadedFile


from docgen_api.models import (
    SubcriptionRequest,
    SubcriptionRequestFile
)
from docgen_api.uitls import (
    process_image_file,
    get_content_type_from
)
from docgen_api.celery_worker.worker import app

_logger = get_task_logger(__name__)

@app.task(name="process_doc_gen_result", queue="doc_gen_rs")
def process_doc_gen_result(rq_id, result):
    # print("rq_id:", rq_id)
    # print("result:", result)
    image_content = result['content'][0]['image']
    gen_image = io.BytesIO(base64.b64decode(image_content))

    report_filter = SubcriptionRequest.objects.filter(
        request_id=rq_id
    )
    if len(report_filter) == 0:
        raise ValueError(f"Number of records is 0")
    rq_record = report_filter[0]

    try:
        file_name = f"gen_{rq_id}.jpg"
        content_type = get_content_type_from(file_name)

        file_obj: TemporaryUploadedFile = TemporaryUploadedFile(
            name=file_name,
            content_type=content_type,
            size=gen_image.getbuffer().nbytes,
            charset='utf-8'
        )
        file_obj.write(gen_image.getvalue())
        file_obj.seek(0)

        b_urls = process_image_file(
            file_name=file_name,
            file_obj=file_obj,
            request=rq_record
        )

        # rq_record.result = [item['file_url'] for item in b_urls]
        rq_record.result = b_urls[0]['file_url'] if len(b_urls) > 0 else ""
        rq_record.status = 2 # PredictCompleted
        rq_record.save()
        return Response(status=status.HTTP_200_OK)
    except Exception as e:
        print(e)
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    