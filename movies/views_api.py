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
    lookup_field = 'slug'

    def get_object(self):
        """
        Returns the object the view is displaying.
        Try to use the slug first, then fall back to pk/id.
        """
        queryset = self.filter_queryset(self.get_queryset())

        # Perform the lookup filtering.
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

        assert lookup_url_kwarg in self.kwargs, (
            'Expected view %s to be called with a URL keyword argument '
            'named "%s". Fix your URL conf, or set the `.lookup_field` '
            'attribute on the view correctly.' %
            (self.__class__.__name__, lookup_url_kwarg)
        )

        value = self.kwargs[lookup_url_kwarg]

        # Try to look up by slug first
        try:
            obj = queryset.get(slug=value)
        except (Movie.DoesNotExist, ValueError):
            try:
                # If that fails, try looking up by ID
                obj = queryset.get(pk=value)
            except (Movie.DoesNotExist, ValueError):
                raise Movie.DoesNotExist('Movie matching query does not exist.')

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj

    def perform_create(self, serializer):
        title = serializer.validated_data.get('title', '')
        slug = slugify(title)
        serializer.save(slug=slug)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated], url_path='favorite', url_name='favorite')
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