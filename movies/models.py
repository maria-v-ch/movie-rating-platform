import uuid
from decimal import ROUND_HALF_UP, Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Avg
from django.utils import timezone
from django.utils.text import slugify


class Movie(models.Model):
    title = models.CharField(max_length=255, db_index=True)
    original_title = models.CharField(max_length=255, blank=True, default="", db_index=True)
    director = models.CharField(max_length=255, db_index=True)
    release_year = models.IntegerField(
        db_index=True,
        validators=[
            MinValueValidator(1888),  # First film ever made
            MaxValueValidator(timezone.now().year + 5),  # Allow for upcoming movies
        ],
    )
    description = models.TextField()
    runtime = models.IntegerField(validators=[MinValueValidator(1)])
    country = models.CharField(max_length=100)
    movement = models.CharField(max_length=100, db_index=True)
    cinematographer = models.CharField(max_length=255, blank=True)
    poster = models.ImageField(upload_to="posters/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    slug = models.SlugField(unique=True, blank=True, db_index=True)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0, db_index=True)
    total_ratings = models.IntegerField(default=0)
    favorited_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL, through="users.UserFavoriteMovie", related_name="favorited_movies", blank=True
    )

    class Meta:
        indexes = [
            models.Index(fields=["title", "release_year"]),
            models.Index(fields=["director", "release_year"]),
            models.Index(fields=["movement", "release_year"]),
            models.Index(fields=["average_rating", "release_year"]),
            models.Index(fields=["slug"]),
            models.Index(fields=["-release_year", "-average_rating"]),
        ]
        ordering = ["-release_year", "-average_rating"]

    @property
    def poster_url(self):
        """Return the URL for the movie poster."""
        # Check for static poster first using the poster filename
        if self.poster:
            return f"/static/movies/posters/{self.poster}"

        # Fallback to default poster
        return "/static/movies/posters/default.jpg"

    def clean(self):
        super().clean()
        if self.release_year and self.release_year < 1888:
            raise ValidationError({"release_year": "Release year cannot be earlier than 1888 (first film ever made)."})
        if self.release_year and self.release_year > timezone.now().year + 5:
            raise ValidationError({"release_year": "Release year cannot be more than 5 years in the future."})
        if self.runtime and self.runtime < 1:
            raise ValidationError({"runtime": "Runtime must be positive."})

    def __str__(self):
        return f"{self.title} ({self.release_year}) - {self.director}"

    def save(self, *args, **kwargs):
        self.full_clean()
        if not self.slug:
            base_slug = slugify(self.title)
            if not Movie.objects.filter(slug=base_slug).exists():
                self.slug = base_slug
            else:
                self.slug = f"{base_slug}-{uuid.uuid4().hex[:8]}"
        super().save(*args, **kwargs)

    def update_rating(self):
        ratings = self.ratings.all()
        if ratings:
            avg_rating = ratings.aggregate(Avg("score"))["score__avg"]
            avg_decimal = Decimal(str(avg_rating)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            self.average_rating = avg_decimal
            self.total_ratings = ratings.count()
        else:
            self.average_rating = Decimal("0.00")
            self.total_ratings = 0
        self.save(update_fields=["average_rating", "total_ratings"])

    @property
    def year(self):
        return self.release_year
