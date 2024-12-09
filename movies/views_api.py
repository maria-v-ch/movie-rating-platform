from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils.text import slugify
from django_filters import rest_framework as django_filters
from .models import Movie
from .serializers import MovieSerializer, DirectorSerializer, MovementSerializer
from .pagination import CustomPagination

class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff

class MovieFilter(django_filters.FilterSet):
    release_year = django_filters.NumberFilter()
    movement = django_filters.CharFilter(lookup_expr='iexact')
    director = django_filters.CharFilter(lookup_expr='iexact')
    
    class Meta:
        model = Movie
        fields = ['release_year', 'movement', 'director']

class MovieViewSet(viewsets.ModelViewSet):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    lookup_field = 'slug'
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = CustomPagination
    filter_backends = [
        django_filters.DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    filterset_class = MovieFilter
    search_fields = ['title', 'director', 'description']
    ordering_fields = ['release_year', 'title']
    ordering = ['-release_year']

    def perform_create(self, serializer):
        title = serializer.validated_data.get('title', '')
        slug = slugify(title)
        serializer.save(slug=slug)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def favorite(self, request, slug=None):
        movie = self.get_object()
        user = request.user
        if movie.favorited_by.filter(id=user.id).exists():
            movie.favorited_by.remove(user)
            return Response({'status': 'unfavorited'})
        else:
            movie.favorited_by.add(user)
            return Response({'status': 'favorited'})

class DirectorViewSet(viewsets.ModelViewSet):
    queryset = Movie.objects.values('director').distinct()
    serializer_class = DirectorSerializer
    permission_classes = [IsAdminOrReadOnly]

class MovementViewSet(viewsets.ModelViewSet):
    queryset = Movie.objects.values('movement').distinct()
    serializer_class = MovementSerializer
    permission_classes = [IsAdminOrReadOnly] 