# Create your views here.
from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from .tasks import generate_image_task
from celery.result import AsyncResult

class GenerateImageView(View):
    def post(self, request):
        data = json.loads(request.body)
        task = generate_image_task.delay(data)
        return JsonResponse({"task_id": task.id}, status=202)

class TaskStatusView(View):
    def get(self, request, task_id):
        task = AsyncResult(task_id)
        if task.state == 'SUCCESS':
            return JsonResponse({"status": task.state, "result": task.result}, status=200)
        else:
            return JsonResponse({"status": task.state}, status=200)
