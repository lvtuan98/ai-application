import logging
import urllib
import urllib.request
from io import BytesIO
from PIL import Image

import base64

import cv2
import numpy as np

_logger = logging.getLogger(__name__)


def encode_image(image):
    image = Image.fromarray(image)
    img_io = BytesIO()
    image.save(img_io, "PNG")
    img_io.seek(0)
    encoded_image = base64.b64encode(img_io.getvalue())
    return encoded_image


def download_img_from_url(url, s3_client=None) -> np.ndarray:
    """Download file from url

    Args:
        url (str): url
    """
    try:
        # if "http" in url:
        img = get_img_from_url(url)
        # else:
        #     img_bytes = get_file_from_s3(s3_client=s3_client, s3_key=url)
        #     pil_img = Image.open(BytesIO(img_bytes))
        #     img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    except Exception as err:
        print(f"Error downloading image from url: {err}")
        return None
    return img


def get_file_bytes_from_url(file_url: str):
    assert file_url is not None and len(file_url) > 0, "file_url is empty"
    bytes_output = None
    try:
        req_url = urllib.request.Request(
            url=file_url, headers={"User-Agent": "Mozilla/5.0"}
        )
        req = urllib.request.urlopen(req_url)
        bytes_output = bytearray(req.read())

        # with urllib.request.urlopen(file_url) as req:
        #     bytes_output = bytearray(req.read())
    except Exception as err:
        _logger.error(f"Error when get file from url: {err}")
    return bytes_output


def get_img_from_url(file_url: str) -> np.ndarray:
    bytes_file = get_file_bytes_from_url(file_url)
    cv2_img = np.asarray(bytearray(bytes_file), dtype=np.uint8)
    cv2_img = cv2.imdecode(cv2_img, cv2.IMREAD_COLOR)
    return cv2_img
