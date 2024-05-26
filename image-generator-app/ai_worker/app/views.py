# Create your views here.
from django.http import JsonResponse
from django.views import View
import json
from .utils.image_processor import generate_image

class GenerateImageView(View):
    def post(self, request):
        data = json.loads(request.body)
        image_data = generate_image(data)
        return JsonResponse({"image_data": image_data}, status=200)
