from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings

class Review(models.Model):
    movie = models.ForeignKey('movies.Movie', on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['movie', '-created_at']),
            models.Index(fields=['user', '-created_at']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['movie', 'user'],
                name='unique_review_per_movie_user'
            )
        ]

    def __str__(self):
        return f'Review by {self.user.username} for {self.movie.title}'

class Rating(models.Model):
    movie = models.ForeignKey('movies.Movie', on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ratings')
    score = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        validators=[
            MinValueValidator(0.0),
            MaxValueValidator(5.0)
        ]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['movie', '-created_at']),
            models.Index(fields=['user', '-created_at']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['movie', 'user'],
                name='unique_rating_per_movie_user'
            )
        ]

    def __str__(self):
        return f'{self.score} stars by {self.user.username} for {self.movie.title}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.movie.update_rating()
