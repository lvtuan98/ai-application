import os
import io
import ast
import uuid
import traceback
from pathlib import Path
from PIL import ExifTags, Image
from typing import Union, Dict, List

from django.core.files.uploadedfile import TemporaryUploadedFile

from .celery_worker.client_connector import c_connector
from docgen import settings
from docgen_api.models import (
    SubcriptionRequest,
    SubcriptionRequestFile
)
from docgen_api.common import (
    FolderFileType,
    ContentType,
    FileExtension
)

def validate_doc_gen_request_and_get(request):
    validated_data = {}
    validated_data["prompt"] = request.data["prompt"]
    validated_data["location"] = request.data["location"]
    list_file = request.data.getlist("file")
    validated_data["file"] = list_file[0]
    return validated_data

def process_image_file(
    file_name: str,
    file_obj: TemporaryUploadedFile,
    request: SubcriptionRequest
):
    file_path = save_file(file_name, request, file_obj)

    new_request_file: SubcriptionRequestFile = SubcriptionRequestFile(
        file_path=file_path,
        file_name=file_name,
        request=request,
        code=f"FIL{uuid.uuid4().hex}",
    )
    new_request_file.save()

    return [{
        "file_url": build_url(
            folder=FolderFileType.REQUESTS.value,
            data_id=request.request_id,
            file_name=file_name
        ),
        "file_path": file_path
    }]

def get_file(file_path: str):
    try:
        return open(file_path, "rb")
    except Exception as e:
        print(e)
        raise SystemError(e)

def save_file(
    file_name: str,
    request: SubcriptionRequest,
    file: TemporaryUploadedFile
):
    try:
        folder_path = get_folder_path(request=request)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path, exist_ok=True)
        return save_file_with_path(file_name=file_name, file=file, folder_path=folder_path)
    except Exception as e:
        print(e)
        raise SystemError(e)



def get_folder_path(request: SubcriptionRequest):
    request_id = str(request.request_id)
    return os.path.join(
        settings.MEDIA_ROOT,
        'requests',
        'doc_gen',
        request_id
    )

def save_file_with_path(
    file_name: str,
    file: TemporaryUploadedFile,
    folder_path: str
):
    try:
        file_path = os.path.join(folder_path, file_name)
        save_img(file_path=file_path, file=file)
        return file_path
    except Exception as e:
        print(e)
        raise SystemError(e)

def save_img(file_path: str, file: TemporaryUploadedFile, quality: str = 100):    
    # with open(file.temporary_file_path(), "rb") as fs:
    # with open(file.name, "rb") as fs:
    input_file = io.BytesIO(file.read())
    image = Image.open(input_file)

    # read orient from metadata. WindowsPhoto keep the origin
    for orientation in ExifTags.TAGS.keys():
        if ExifTags.TAGS[orientation] == "Orientation":
            break
    try:
        e = image._getexif()  # returns None if no EXIF data
        if e:
            exif = dict(e.items())
            if orientation in exif:
                orientation = exif[orientation]
                if orientation == 3:
                    image = image.transpose(Image.ROTATE_180)
                elif orientation == 6:
                    image = image.transpose(Image.ROTATE_270)
                elif orientation == 8:
                    image = image.transpose(Image.ROTATE_90)
    except Exception as ex:
        print(ex)
        print("Rotation Error")
        traceback.print_exc()
    image.convert("RGB").save(file_path, optimize=True, quality=quality)

def build_url(
    folder: str,
    data_id: str,
    file_name: str,
    use_base_url: bool = True
):
    base_url = "" if not use_base_url else settings.BASE_URL
    return "{base_url}/api/idp/media/{folder}/{uid}/?file_name={file_name}".format(
        base_url=base_url,
        folder=folder,
        uid=data_id,
        file_name=file_name
    )

def send_to_queue(
    request_id: str,
    file_info: Union[dict | List[dict]],
    prompt: str,
    location: List[int]
):
    file_info = [item['file_url'] for item in file_info]
    print(
        f"Send to queue: {request_id} - {file_info} - {prompt} - {location}"
    )

    try:
        location = ast.literal_eval(location)
        c_connector.process_doc_gen((request_id, file_info, prompt, location))
    except Exception as e:
        print(e)
        raise SystemError(e)
    
def get_content_type_from(filename: Union[str, Path]):
    if isinstance(filename, str):
        filename = Path(filename)
    suffix = filename.suffix.lower()
    if suffix in FileExtension.PDF.value:
        return ContentType.PDF.value
    elif suffix in FileExtension.XLSX.value:
        return ContentType.XLSX.value
    elif suffix in FileExtension.IMG.value:
        return ContentType.IMG.value
    else:
        raise Exception(f"Not found content type for {suffix}")