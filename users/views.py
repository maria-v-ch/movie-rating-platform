from django.views.generic import CreateView, UpdateView, DetailView, ListView
from django.contrib.auth.views import LoginView as AuthLoginView, LogoutView as AuthLogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import User
from .forms import UserRegistrationForm, UserUpdateForm
from .serializers import UserSerializer, UserCreateSerializer, UserUpdateSerializer

class RegisterView(SuccessMessageMixin, CreateView):
    template_name = 'users/register.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('users:login')
    success_message = "Your account was created successfully. Please log in."

class LoginView(AuthLoginView):
    template_name = 'users/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return reverse_lazy('movies:movie-list')

class LogoutView(AuthLogoutView):
    next_page = reverse_lazy('movies:movie-list')

class ProfileView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'users/profile.html'
    context_object_name = 'profile_user'

    def get_object(self):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        context['reviews'] = user.reviews.select_related('movie').order_by('-created_at')[:5]
        context['ratings'] = user.ratings.select_related('movie').order_by('-created_at')[:5]
        return context

class ProfileUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = User
    template_name = 'users/profile_edit.html'
    form_class = UserUpdateForm
    success_url = reverse_lazy('users:profile')
    success_message = "Your profile was updated successfully."

    def get_object(self):
        return self.request.user

class FavoritesView(LoginRequiredMixin, ListView):
    template_name = 'users/favorites.html'
    context_object_name = 'favorite_movies'

    def get_queryset(self):
        return self.request.user.favorite_movies.all()

# API Views
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action == 'update' or self.action == 'partial_update':
            return UserUpdateSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        return super().get_permissions()

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return User.objects.all()
        return User.objects.filter(id=user.id)

    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['put'])
    def update_me(self, request):
        serializer = UserUpdateSerializer(request.user, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 