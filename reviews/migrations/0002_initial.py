# Generated by Django 5.1.4 on 2024-12-09 18:51

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('movies', '0002_initial'),
        ('reviews', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='rating',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ratings', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='review',
            name='movie',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='movies.movie'),
        ),
        migrations.AddField(
            model_name='review',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddIndex(
            model_name='rating',
            index=models.Index(fields=['movie', '-created_at'], name='reviews_rat_movie_i_2f628a_idx'),
        ),
        migrations.AddIndex(
            model_name='rating',
            index=models.Index(fields=['user', '-created_at'], name='reviews_rat_user_id_3ac4e3_idx'),
        ),
        migrations.AddConstraint(
            model_name='rating',
            constraint=models.UniqueConstraint(fields=('movie', 'user'), name='unique_rating_per_movie_user'),
        ),
        migrations.AddIndex(
            model_name='review',
            index=models.Index(fields=['movie', '-created_at'], name='reviews_rev_movie_i_79ac9e_idx'),
        ),
        migrations.AddIndex(
            model_name='review',
            index=models.Index(fields=['user', '-created_at'], name='reviews_rev_user_id_eeecea_idx'),
        ),
        migrations.AddConstraint(
            model_name='review',
            constraint=models.UniqueConstraint(fields=('movie', 'user'), name='unique_review_per_movie_user'),
        ),
    ]