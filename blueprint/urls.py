from rest_framework import routers
from django.urls import path, include
from .views import ProjectViewSet, FloorplanViewSet

router = routers.DefaultRouter()
router.register(r"projects", ProjectViewSet)
router.register(r"floorplans", FloorplanViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
