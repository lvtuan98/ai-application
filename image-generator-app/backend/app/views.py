# Create your views here.
from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from .tasks import generate_image_task
from celery.result import AsyncResult
import os
import requests
from dotenv import load_dotenv
load_dotenv()

AI_WORKER_URL = os.environ.get("AI_WORKER_URL", "http://localhost:5001")

class StartedView(View):
    def get(self, request):
        return JsonResponse({'message': 'I am a Backend'})

class GenerateImageView(View):
    def post(self, request):
        data = json.loads(request.body)
        print(data, flush=True)
        input_data = {
            "text": data['data'],
            "options": ""
        }
        print(input_data)
        print(f"{AI_WORKER_URL}/generate/")
        response = requests.post(f"{AI_WORKER_URL}/generate/", json=input_data, verify=False)
        print(response.content)
        return response.content, response.status_code

        # task = generate_image_task.delay(data)
        # return JsonResponse({"task_id": task.id}, status=202)

class TaskStatusView(View):
    def get(self, request, task_id):
        task = AsyncResult(task_id)
        if task.state == 'SUCCESS':
            return JsonResponse({"status": task.state, "result": task.result}, status=200)
        else:
            return JsonResponse({"status": task.state}, status=200)
