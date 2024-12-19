# pylint: disable=relative-beyond-top-level
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView as AuthLoginView
from django.contrib.auth.views import LogoutView as AuthLogoutView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .forms import UserRegistrationForm, UserUpdateForm
from .serializers import UserCreateSerializer, UserSerializer, UserUpdateSerializer

User = get_user_model()


class RegisterView(SuccessMessageMixin, CreateView):
    template_name = "users/register.html"
    form_class = UserRegistrationForm
    success_url = reverse_lazy("users:login")
    success_message = "Your account was created successfully. Please log in."


class LoginView(AuthLoginView):
    template_name = "users/login.html"
    redirect_authenticated_user = True

    def get_success_url(self):
        next_url = self.request.GET.get("next")
        if next_url:
            return next_url
        return reverse_lazy("movies:movie-list")


class LogoutView(AuthLogoutView):
    next_page = reverse_lazy("movies:movie-list")


class ProfileView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = "users/profile.html"
    fields = ["email", "bio", "profile_image"]
    success_url = reverse_lazy("users:profile")

    def get_object(self):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        context["reviews"] = user.reviews.select_related("movie").order_by("-created_at")[:5]
        context["ratings"] = user.ratings.select_related("movie").order_by("-created_at")[:5]
        return context

    def form_valid(self, form):
        messages.success(self.request, "Profile updated successfully!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Error updating profile. Please check the form.")
        return super().form_invalid(form)


class ProfileUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = User
    template_name = "users/profile.html"
    form_class = UserUpdateForm
    success_url = reverse_lazy("users:profile")
    success_message = "Your profile was updated successfully."

    def get_object(self):
        return self.request.user


class FavoritesView(LoginRequiredMixin, ListView):
    template_name = "users/favorites.html"
    context_object_name = "favorite_movies"

    def get_queryset(self):
        return self.request.user.favorited_movies.all()


# API Views
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer
        if self.action in ["update", "partial_update"]:
            return UserUpdateSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action == "create":
            return [permissions.AllowAny()]
        if self.action in ["list", "retrieve"]:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return User.objects.none()
        if user.is_staff:
            return User.objects.all()
        return User.objects.filter(id=user.id)

    @action(detail=False, methods=["get"], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=["put", "patch"], permission_classes=[permissions.IsAuthenticated])
    def update_me(self, request):
        serializer = UserUpdateSerializer(request.user, data=request.data, context={"request": request}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
