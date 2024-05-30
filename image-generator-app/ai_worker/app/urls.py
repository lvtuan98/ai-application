from django.urls import path
from .views import GenerateImageView, StartedView

urlpatterns = [
    path('', StartedView.as_view(), name='get_started'),
    path('generate/', GenerateImageView.as_view(), name='generate_image'),
]
