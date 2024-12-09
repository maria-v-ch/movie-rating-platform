from django.views.generic import ListView, DetailView
from django.db.models import Q, Count
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters import rest_framework as django_filters
from .models import Movie
from .serializers import MovieSerializer
from django.utils.html import escape
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

class MovieListView(ListView):
    model = Movie
    template_name = 'movies/movie_list.html'
    context_object_name = 'movies'
    paginate_by = 12

    def get_queryset(self):
        queryset = Movie.objects.all()
        search = self.request.GET.get('search')
        movement = self.request.GET.get('movement')
        director = self.request.GET.get('director')
        sort = self.request.GET.get('sort', '-release_year')

        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(director__icontains=search) |
                Q(description__icontains=search)
            )
        if movement:
            queryset = queryset.filter(movement=movement)
        if director:
            queryset = queryset.filter(director=director)

        return queryset.order_by(sort)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['movements'] = Movie.objects.values('movement').distinct()
        context['directors'] = Movie.objects.values('director').distinct()
        return context

class MovieDetailView(DetailView):
    model = Movie
    template_name = 'movies/movie_detail.html'
    context_object_name = 'movie'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        movie = self.get_object()
        context['similar_movies'] = Movie.objects.filter(
            Q(director=movie.director) | Q(movement=movie.movement)
        ).exclude(id=movie.id)[:4]
        context['reviews'] = movie.reviews.select_related('user').order_by('-created_at')[:5]
        return context

class DirectorListView(ListView):
    model = Movie
    template_name = 'movies/director_list.html'
    context_object_name = 'directors'

    def get_queryset(self):
        return Movie.objects.values('director').annotate(
            movie_count=Count('id')
        ).order_by('director')

class MovementListView(ListView):
    model = Movie
    template_name = 'movies/movement_list.html'
    context_object_name = 'movements'

    def get_queryset(self):
        return Movie.objects.values('movement').annotate(
            movie_count=Count('id')
        ).order_by('movement')

# API Views
class MovieViewSet(viewsets.ModelViewSet):
    queryset = Movie.objects.all()
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
    serializer_class = MovieSerializer

    def perform_create(self, serializer):
        # Escape HTML in text fields
        data = serializer.validated_data
        if 'title' in data:
            data['title'] = escape(data['title'])
        if 'description' in data:
            data['description'] = escape(data['description'])
        serializer.save()

    def perform_update(self, serializer):
        # Escape HTML in text fields
        data = serializer.validated_data
        if 'title' in data:
            data['title'] = escape(data['title'])
        if 'description' in data:
            data['description'] = escape(data['description'])
        serializer.save()

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