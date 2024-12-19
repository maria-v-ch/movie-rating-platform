# pylint: disable=relative-beyond-top-level
from django.urls import path

from movies import views

app_name = "movies"

urlpatterns = [
    path("", views.MovieListView.as_view(), name="movie-list"),
    path("movies/<slug:slug>/", views.MovieDetailView.as_view(), name="movie-detail"),
    path("directors/", views.DirectorListView.as_view(), name="directors"),
    path("movements/", views.MovementListView.as_view(), name="movements"),
]
