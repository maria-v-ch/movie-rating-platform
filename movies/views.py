from django.views.generic import ListView, DetailView
from django.db.models import Q, Count, Avg
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
        
        # Filter by director if specified
        director = self.request.GET.get('director')
        if director:
            queryset = queryset.filter(director=director)
        
        # Filter by movement if specified
        movement = self.request.GET.get('movement')
        if movement:
            queryset = queryset.filter(movement=movement)
        
        # Filter by year if specified
        year = self.request.GET.get('year')
        if year:
            queryset = queryset.filter(release_year=year)
        
        return queryset.order_by('-release_year', '-average_rating')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get unique directors with their movie counts
        context['directors'] = (Movie.objects.values('director')
                              .annotate(movie_count=Count('id'))
                              .order_by('director')
                              .distinct())
        
        # Get unique movements with their movie counts
        context['movements'] = (Movie.objects.values('movement')
                              .annotate(movie_count=Count('id'))
                              .order_by('movement')
                              .distinct())
        
        # Get unique years
        context['years'] = (Movie.objects.values_list('release_year', flat=True)
                          .order_by('-release_year')
                          .distinct())
        
        # Get current filters
        context['current_director'] = self.request.GET.get('director', '')
        context['current_movement'] = self.request.GET.get('movement', '')
        context['current_year'] = self.request.GET.get('year', '')
        
        return context

class MovieDetailView(DetailView):
    model = Movie
    template_name = 'movies/movie_detail.html'
    context_object_name = 'movie'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        movie = self.get_object()
        
        # Get reviews with related user and rating data
        reviews = movie.reviews.select_related('user').prefetch_related(
            'user__ratings'
        ).order_by('-created_at')[:5]
        
        # Create a dictionary of user ratings for this movie
        user_ratings = {}
        for review in reviews:
            rating = review.user.ratings.filter(movie=movie).first()
            if rating:
                user_ratings[review.user.id] = rating
        
        context['reviews'] = reviews
        context['user_ratings'] = user_ratings
        context['similar_movies'] = Movie.objects.filter(
            Q(director=movie.director) | Q(movement=movie.movement)
        ).exclude(id=movie.id)[:4]
        
        # Add user's review and rating if authenticated
        if self.request.user.is_authenticated:
            context['user_review'] = movie.reviews.filter(user=self.request.user).first()
            context['user_rating'] = movie.ratings.filter(user=self.request.user).first()
        
        return context

class DirectorListView(ListView):
    template_name = 'movies/director_list.html'
    context_object_name = 'directors'

    def get_queryset(self):
        return (Movie.objects.values('director')
                .annotate(
                    movie_count=Count('id'),
                    rated_count=Count('ratings'),
                    avg_rating=Avg('ratings__score')
                )
                .order_by('director')
                .distinct())

class MovementListView(ListView):
    template_name = 'movies/movement_list.html'
    context_object_name = 'movements'

    def get_queryset(self):
        return (Movie.objects.values('movement')
                .annotate(
                    movie_count=Count('id'),
                    rated_count=Count('ratings'),
                    avg_rating=Avg('ratings__score')
                )
                .order_by('movement')
                .distinct())

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