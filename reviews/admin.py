from django.contrib import admin
from .models import Review, Rating

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('movie', 'user', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('movie__title', 'user__username', 'text')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('movie', 'user')

@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('movie', 'user', 'score', 'created_at')
    list_filter = ('score', 'created_at')
    search_fields = ('movie__title', 'user__username')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('movie', 'user')
