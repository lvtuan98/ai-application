import uuid
from django.db import models
from django.utils import timezone
from .common import FileCategory


# Create your models here.
class SubcriptionRequest(models.Model):
    id = models.AutoField(primary_key=True)
    request_id = models.CharField(max_length=200)
    prompt = models.CharField(max_length=200, null=True)
    location = models.JSONField(null=True)
    provider_code = models.CharField(max_length=200, default="DG")
    result = models.CharField(max_length=200)
    status = (
        models.IntegerField()
    ) # 1: Processing(Pending) 2: PredictCompleted 3: ReturnCompleted
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

class SubcriptionRequestFile(models.Model):
    def get_new_code():
        return f"FIL{uuid.uuid4().hex}"

    code = models.CharField(max_length=300, default=get_new_code)
    file_name = models.CharField(max_length=300, default=None)
    file_path = models.CharField(max_length=500, default=None)
    file_category = models.CharField(
        max_length=200, default=FileCategory.Origin.value
    )
    request = models.ForeignKey(
        SubcriptionRequest, related_name="files", on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)