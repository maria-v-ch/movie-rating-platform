# pylint: disable=relative-beyond-top-level
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "reviews"

router = DefaultRouter()
router.register("reviews", views.ReviewViewSet, basename="review")
router.register("ratings", views.RatingViewSet, basename="rating")

urlpatterns = [
    path("", include(router.urls)),
]
