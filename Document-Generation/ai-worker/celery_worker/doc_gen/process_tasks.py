import sys
import logging
from typing import List
from celery.utils.log import get_task_logger
from rest_framework.response import Response
from rest_framework import status

from celery_worker.doc_gen.worker import app
from celery_worker.doc_gen.client_connector import CeleryConnector
from utils.file import (
    download_img_from_url,
    encode_image
) 


_logger = get_task_logger(__name__)

from pipelines.test import draw_text
# from pipelines.doc_gen import get_pipeline
# processor, pipe = get_pipeline()


@app.task(name="process_doc_gen", queue="doc_gen")
def process_doc_gen(rq_id: str, img_urls: List[str], prompt:str, location: list):
    # print(f"rq_id: {rq_id}")
    # print(f"img_urls: {img_urls}")
    # print(f"prompt: {prompt}")
    # print(f"location: {location}")

    c_connector = CeleryConnector()

    outputs: List[str] = []
    images = [download_img_from_url(img_url) for img_url in img_urls]
    try:
        for idx, cv_image in enumerate(images):
            if cv_image is None:
                raise Exception(
                    f"Failed to download image from url: {img_urls[idx]}"
                )
            gen_image = draw_text(prompt)
            # gen_image = cv_image
            encoded_image = encode_image(gen_image)

            outputs.append({
                "image": encoded_image
            })

        results = {
            "status": 200,
            "content": outputs,
        }
        c_connector.process_doc_gen_result((rq_id, results))
    except Exception as err:
        _logger.error(f"Error in process_doc_gen_result: {err}")
        results = {
            "status": 404,
            "content": {},
        }
        c_connector.process_doc_gen_result((rq_id, results))