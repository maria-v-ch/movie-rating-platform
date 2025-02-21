# Generated by Django 5.1.4 on 2024-12-12 19:36

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("movies", "0002_initial"),
        ("users", "0002_user_bio_user_profile_image"),
    ]

    operations = [
        migrations.AlterField(
            model_name="userfavoritemovie",
            name="movie",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, related_name="user_favorites", to="movies.movie"
            ),
        ),
        migrations.AlterField(
            model_name="userfavoritemovie",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, related_name="user_favorites", to=settings.AUTH_USER_MODEL
            ),
        ),
    ]
