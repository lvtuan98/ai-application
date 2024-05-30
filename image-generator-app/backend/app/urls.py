from django.urls import path
from .views import GenerateImageView, TaskStatusView, StartedView

urlpatterns = [
    path('', StartedView.as_view(), name='get_started'),
    path('generate/', GenerateImageView.as_view(), name='generate_image'),
    path('status/<str:task_id>/', TaskStatusView.as_view(), name='task_status'),
]
