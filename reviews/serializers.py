from rest_framework import serializers
from .models import Review, Rating
from movies.models import Movie
from movies.serializers import MovieListSerializer
from django.contrib.auth import get_user_model
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

User = get_user_model()

class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    movie = MovieListSerializer(read_only=True)
    movie_id = serializers.IntegerField(write_only=True)
    score = serializers.DecimalField(
        max_digits=3,
        decimal_places=1,
        min_value=Decimal('0.0'),
        max_value=Decimal('5.0'),
        required=True,
        write_only=True
    )
    rating_score = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Review
        fields = [
            'id', 'movie', 'movie_id', 'user', 'text',
            'created_at', 'updated_at', 'score', 'rating_score'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_rating_score(self, instance):
        try:
            rating = Rating.objects.get(movie=instance.movie, user=instance.user)
            return str(rating.score)
        except Rating.DoesNotExist:
            return None

    def validate_score(self, value):
        try:
            score = Decimal(str(value)).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP)
            if score < Decimal('0.0') or score > Decimal('5.0'):
                raise serializers.ValidationError("Score must be between 0 and 5.")
            return score
        except (InvalidOperation, TypeError):
            raise serializers.ValidationError("Invalid score format. Must be a decimal number.")

    def create(self, validated_data):
        user = self.context['request'].user
        score = validated_data.pop('score')  # Remove score from review data
        movie_id = validated_data.pop('movie_id')
        movie = Movie.objects.get(id=movie_id)
        validated_data['movie'] = movie
        validated_data['user'] = user
        
        # Check for existing review
        if Review.objects.filter(movie=movie, user=user).exists():
            raise serializers.ValidationError({'detail': 'You have already reviewed this movie.'})
        
        review = super().create(validated_data)
        
        # Create or update the rating
        Rating.objects.update_or_create(
            movie=review.movie,
            user=review.user,
            defaults={'score': score}
        )
        
        review.movie.update_rating()
        return review

    def update(self, instance, validated_data):
        if 'score' in validated_data:
            score = validated_data.pop('score')
            # Update the associated rating
            Rating.objects.update_or_create(
                movie=instance.movie,
                user=instance.user,
                defaults={'score': score}
            )
            instance.movie.update_rating()
        
        # Update the review
        review = super().update(instance, validated_data)
        return review

class RatingSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    movie = MovieListSerializer(read_only=True)
    movie_id = serializers.IntegerField(write_only=True)
    score = serializers.DecimalField(
        max_digits=3,
        decimal_places=1,
        min_value=Decimal('0.0'),
        max_value=Decimal('5.0')
    )
    
    class Meta:
        model = Rating
        fields = [
            'id', 'movie', 'movie_id', 'user', 'score',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate_score(self, value):
        try:
            score = Decimal(str(value)).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP)
            if score < Decimal('0.0') or score > Decimal('5.0'):
                raise serializers.ValidationError("Score must be between 0 and 5.")
            return score
        except (InvalidOperation, TypeError):
            raise serializers.ValidationError("Invalid score format. Must be a decimal number.")

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        movie_id = validated_data.pop('movie_id')
        validated_data['movie'] = Movie.objects.get(id=movie_id)
        rating = super().create(validated_data)
        rating.movie.update_rating()
        return rating

    def update(self, instance, validated_data):
        rating = super().update(instance, validated_data)
        rating.movie.update_rating()
        return rating 