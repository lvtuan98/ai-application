from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter
from docgen_api.views import DocGenViewSet

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register("idp", DocGenViewSet, basename="IDP-DocGen")
app_name = "api"
urlpatterns = router.urls

