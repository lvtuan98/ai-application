# Create your views here.
from django.http import JsonResponse
from django.views import View
import json
import base64
from io import BytesIO

from app.utils.image_processor import generate_image

class StartedView(View):
    def get(self, request):
        return JsonResponse({'message': 'I am an AI worker'})

class GenerateImageView(View):
    def post(self, request):
        data = json.loads(request.body)
        text = data.get("text")
        options = data.get("options", {})
        image_data = generate_image(text, options)
        img_io = BytesIO()
        image_data.save(img_io, "PNG")
        img_io.seek(0)
        encoded_image = base64.b64encode(img_io.getvalue()).decode('utf-8')
        return JsonResponse({"image_data": encoded_image}, status=200)