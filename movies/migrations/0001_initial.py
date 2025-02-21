# Generated by Django 5.1.4 on 2024-12-09 18:51

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Movie",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(db_index=True, max_length=255)),
                ("original_title", models.CharField(blank=True, db_index=True, max_length=255, null=True)),
                ("director", models.CharField(db_index=True, max_length=255)),
                (
                    "release_year",
                    models.IntegerField(
                        db_index=True,
                        validators=[
                            django.core.validators.MinValueValidator(1888),
                            django.core.validators.MaxValueValidator(2029),
                        ],
                    ),
                ),
                ("description", models.TextField()),
                ("runtime", models.IntegerField(validators=[django.core.validators.MinValueValidator(1)])),
                ("country", models.CharField(max_length=100)),
                ("movement", models.CharField(db_index=True, max_length=100)),
                ("cinematographer", models.CharField(blank=True, max_length=255)),
                ("poster", models.ImageField(blank=True, null=True, upload_to="posters/")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("slug", models.SlugField(blank=True, unique=True)),
                ("average_rating", models.DecimalField(db_index=True, decimal_places=2, default=0.0, max_digits=3)),
                ("total_ratings", models.IntegerField(default=0)),
            ],
            options={
                "ordering": ["-release_year", "-average_rating"],
            },
        ),
    ]
