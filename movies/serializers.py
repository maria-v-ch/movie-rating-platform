# pylint: disable=relative-beyond-top-level,unused-import,abstract-method,arguments-renamed,no-name-in-module
from django.core.validators import RegexValidator
from django.utils.html import escape
from rest_framework import serializers

from .models import Movie


class MovieSerializer(serializers.ModelSerializer):
    title = serializers.CharField(validators=[RegexValidator(r"^[^<>]*$", "HTML tags are not allowed")])
    description = serializers.CharField(validators=[RegexValidator(r"^[^<>]*$", "HTML tags are not allowed")])
    director = serializers.CharField(validators=[RegexValidator(r"^[^<>]*$", "HTML tags are not allowed")])
    movement = serializers.CharField(validators=[RegexValidator(r"^[^<>]*$", "HTML tags are not allowed")])
    country = serializers.CharField(validators=[RegexValidator(r"^[^<>]*$", "HTML tags are not allowed")])

    def validate(self, data):
        # Clean all text fields
        for field in ["title", "description", "director", "movement", "country"]:
            if field in data:
                data[field] = escape(str(data[field]))
        return data

    class Meta:
        model = Movie
        fields = ["id", "title", "director", "release_year", "description", "runtime", "country", "movement", "slug"]
        read_only_fields = ["slug"]


class MovieListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = ["id", "title", "director", "release_year", "slug"]
        read_only_fields = ["slug"]


class DirectorSerializer(serializers.Serializer):
    director = serializers.CharField(validators=[RegexValidator(r"^[^<>]*$", "HTML tags are not allowed")])

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if "director" in data and data["director"]:
            data["director"] = escape(str(data["director"]))
        return data


class MovementSerializer(serializers.Serializer):
    movement = serializers.CharField(validators=[RegexValidator(r"^[^<>]*$", "HTML tags are not allowed")])

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if "movement" in data and data["movement"]:
            data["movement"] = escape(str(data["movement"]))
        return data
