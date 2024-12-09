from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.db.models import Avg

class User(AbstractUser):
    email = models.EmailField(_('email address'), unique=True)
    
    # Make first_name and last_name not required
    first_name = None
    last_name = None

    class Meta:
        ordering = ['-date_joined']
        indexes = [
            models.Index(fields=['username']),
            models.Index(fields=['email']),
        ]

    def __str__(self):
        return self.username

    @property
    def total_reviews(self):
        return self.reviews.count()

    @property
    def average_rating_given(self):
        avg = self.ratings.aggregate(Avg('score'))['score__avg']
        return round(avg, 1) if avg is not None else None

class UserFavoriteMovie(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey('movies.Movie', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'movie')
        ordering = ['-created_at']