from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Avg
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    email = models.EmailField(_("email address"), unique=True)
    bio = models.TextField(max_length=500, blank=True)
    profile_image = models.ImageField(upload_to="profile_images/", null=True, blank=True)

    # Make first_name and last_name not required
    first_name = None
    last_name = None

    class Meta:
        ordering = ["-date_joined"]
        indexes = [
            models.Index(fields=["username"]),
            models.Index(fields=["email"]),
        ]

    def __str__(self):
        return self.username

    @property
    def total_reviews(self):
        return self.reviews.count()

    @property
    def average_rating_given(self):
        avg = self.ratings.aggregate(Avg("score"))["score__avg"]
        return round(avg, 1) if avg is not None else None

    @property
    def favorite_movies(self):
        return self.favorited_movies.all()


class UserFavoriteMovie(models.Model):
    user = models.ForeignKey(User, related_name="user_favorites", on_delete=models.CASCADE)
    movie = models.ForeignKey("movies.Movie", related_name="user_favorites", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "movie")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username}'s favorite: {self.movie.title}"
