# pylint: disable=relative-beyond-top-level
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from movies import views_api

router = DefaultRouter()
router.register(r"movies", views_api.MovieViewSet, basename="movie")
router.register(r"directors", views_api.DirectorViewSet, basename="director")
router.register(r"movements", views_api.MovementViewSet, basename="movement")

urlpatterns = [
    path("", include(router.urls)),
]
