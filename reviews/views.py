# pylint: disable=relative-beyond-top-level
from django.shortcuts import get_object_or_404
from rest_framework import filters, permissions, serializers, viewsets
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework_simplejwt.authentication import JWTAuthentication

from movies.models import Movie

from .models import Rating, Review
from .permissions import IsOwnerOrReadOnly
from .serializers import RatingSerializer, ReviewSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    authentication_classes = [JWTAuthentication, SessionAuthentication, BasicAuthentication]
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        queryset = Review.objects.select_related("user", "movie")
        movie_id = self.request.query_params.get("movie")
        user_id = self.request.query_params.get("user")

        if movie_id:
            queryset = queryset.filter(movie_id=movie_id)
        if user_id:
            queryset = queryset.filter(user_id=user_id)

        return queryset

    def perform_create(self, serializer):
        # Get movie_id from either JSON or form data
        movie_id = self.request.data.get("movie_id")
        if not movie_id:
            raise serializers.ValidationError({"movie_id": "This field is required."})

        movie = get_object_or_404(Movie, id=movie_id)

        # Check if user already reviewed this movie
        if Review.objects.filter(movie=movie, user=self.request.user).exists():
            raise serializers.ValidationError({"detail": "You have already reviewed this movie."})

        # Save the review with the user and movie
        serializer.save(user=self.request.user, movie=movie)

    def check_object_permissions(self, request, obj):
        """Explicitly check object permissions"""
        super().check_object_permissions(request, obj)
        if not self.get_permissions()[1].has_object_permission(request, self, obj):
            self.permission_denied(request)


class RatingViewSet(viewsets.ModelViewSet):
    serializer_class = RatingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    authentication_classes = [JWTAuthentication, SessionAuthentication, BasicAuthentication]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["created_at", "score"]
    ordering = ["-created_at"]

    def get_queryset(self):
        queryset = Rating.objects.select_related("user", "movie")
        movie_id = self.request.query_params.get("movie_id")
        user_id = self.request.query_params.get("user_id")

        if movie_id:
            queryset = queryset.filter(movie_id=movie_id)
        if user_id:
            queryset = queryset.filter(user_id=user_id)

        return queryset

    def perform_create(self, serializer):
        movie = get_object_or_404(Movie, id=serializer.validated_data["movie_id"])
        # Update or create rating
        rating, _ = Rating.objects.update_or_create(
            movie=movie, user=self.request.user, defaults={"score": serializer.validated_data["score"]}
        )
        movie.update_rating()
        serializer.instance = rating  # Set the instance so it's included in the response
        return rating

    def perform_destroy(self, instance):
        movie = instance.movie
        super().perform_destroy(instance)
        # Force a refresh from the database to ensure we have the latest state
        movie.refresh_from_db()
        movie.update_rating()

    def check_object_permissions(self, request, obj):
        """Explicitly check object permissions"""
        super().check_object_permissions(request, obj)
        if not self.get_permissions()[1].has_object_permission(request, self, obj):
            self.permission_denied(request)
