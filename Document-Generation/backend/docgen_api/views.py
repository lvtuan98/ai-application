import time
import uuid

from django.shortcuts import render

from rest_framework import status, viewsets
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action
from django.core.files.uploadedfile import TemporaryUploadedFile
from django.http import HttpResponse
from wsgiref.util import FileWrapper



from docgen import settings
from docgen_api.models import (
    SubcriptionRequest,
    SubcriptionRequestFile
)
from docgen_api.serializer import ReportSerializer
from docgen_api.uitls import (
    validate_doc_gen_request_and_get,
    process_image_file,
    send_to_queue,
    get_content_type_from,
    get_file
)


# Create your views here.


class DocGenViewSet(viewsets.ViewSet):
    @extend_schema(
        request = {
            "multipart/form-data": {
                "type": "object",
                "properties": {
                    "file": {"type": "string", "format": "binary"},
                    "location": {"type": "string"},
                    "prompt": {"type": "string"}
                },
                "required": {"file", "location", "prompt"},
            }
        },
        responses = None,
        tags = ['Doc Gen'],
        description = """
            Document Generation
        """
    )
    @action(detail=False, url_path="image/generate", methods=["POST"])
    def generate(self, request):
        provider_code = settings.PROVIDED_CODE

        validated_data = validate_doc_gen_request_and_get(request)
        rq_id = f'{provider_code}_{time.strftime("%Y%m%d_%H%M%S")}_{uuid.uuid4().hex}'

        file_obj: TemporaryUploadedFile = validated_data['file']
        prompt = validated_data['prompt']
        location = validated_data['location']
        file_extension = file_obj.name.split(".")[-1]
        file_name = f"temp_{rq_id}.{file_extension}"

        new_request: SubcriptionRequest = SubcriptionRequest(
            request_id = rq_id,
            prompt = prompt,
            location = location,
            provider_code = provider_code,
            status=1,
        )
        new_request.save()

        b_urls = process_image_file(
            file_name=file_name,
            file_obj=file_obj,
            request=new_request
        )

        send_to_queue(request_id=rq_id, file_info=b_urls, prompt=prompt, location=location)
        return Response(status=status.HTTP_200_OK, data=rq_id)
    
    @extend_schema(request=None, responses=None, tags=["Doc Gen"])
    @action(detail=False, url_path=r"result/(?P<request_id>\w+)", methods=["GET"])
    def get_result(self, request, request_id=None):
        if request_id is None:
            raise ValueError(f"{request_id} is None")
        report_filter = SubcriptionRequest.objects.filter(
            request_id=request_id
        )

        if len(report_filter) == 0:
            raise ValueError(f"No record is matched with {request_id}")
                    
        serializer: ReportSerializer = ReportSerializer(
            data=report_filter, many=True
        )
        serializer.is_valid()
        return Response(status=status.HTTP_200_OK, data=serializer.data[0])

    @extend_schema(request=None, responses=None, tags=["data"])
    @action(
        detail=False,
        url_path=r"media/(?P<folder_type>\w+)/(?P<uq_id>\w+)",
        methods=["GET"],
    )
    def get_file_v2(self, request, uq_id=None, folder_type=None):
        content_type = "image/png"
        file_name: str = request.query_params.get("file_name", None)
        if folder_type is None:
            raise ValueError(f"Folder type {folder_type} is None")
        if uq_id is None:
            raise ValueError(f"Request ID {uq_id} is None")

        if folder_type == "requests":
            if file_name is None:
                raise ValueError(f"File name {file_name} is None")
            try:
                rqs = SubcriptionRequest.objects.filter(request_id=uq_id)
                if len(rqs) != 1:
                    raise ValueError(f"Number of results is not equal 1")
                rq = rqs[0]

                content_type = get_content_type_from(file_name)

                file_data = SubcriptionRequestFile.objects.filter(
                    request=rq, file_name=file_name
                )[0]

            except IndexError:
                raise SystemError()
            return HttpResponse(
                FileWrapper(get_file(file_data.file_path)),
                status=status.HTTP_200_OK,
                headers={
                    "Content-Disposition": "filename={fn}".format(
                        fn=file_data.file_name
                    )
                },
                content_type=content_type,
            )
        else:
            raise SystemError()
