# pylint: disable=relative-beyond-top-level
from django_filters import rest_framework as django_filters

from .models import Movie


class MovieFilter(django_filters.FilterSet):
    release_year = django_filters.NumberFilter()
    movement = django_filters.CharFilter(lookup_expr="iexact")
    director = django_filters.CharFilter(lookup_expr="iexact")

    class Meta:
        model = Movie
        fields = ["release_year", "movement", "director"]
