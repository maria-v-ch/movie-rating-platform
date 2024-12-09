from django.contrib import admin
from .models import Movie

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'director', 'release_year', 'movement', 'average_rating', 'total_ratings')
    list_filter = ('movement', 'release_year', 'director')
    search_fields = ('title', 'director', 'description')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('average_rating', 'total_ratings', 'created_at', 'updated_at')
    ordering = ('-release_year', '-average_rating')
    
    fieldsets = (
        (None, {
            'fields': ('title', 'original_title', 'slug', 'director', 'release_year')
        }),
        ('Details', {
            'fields': ('description', 'runtime', 'country', 'movement', 'cinematographer', 'poster')
        }),
        ('Statistics', {
            'fields': ('average_rating', 'total_ratings'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    ) 