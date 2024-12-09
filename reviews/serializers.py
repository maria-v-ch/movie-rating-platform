from rest_framework import serializers
from .models import Review, Rating
from movies.serializers import MovieListSerializer
from decimal import Decimal, InvalidOperation

class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    movie = MovieListSerializer(read_only=True)
    movie_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Review
        fields = [
            'id', 'movie', 'movie_id', 'user', 'text',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class RatingSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    movie = MovieListSerializer(read_only=True)
    movie_id = serializers.IntegerField(write_only=True)
    score = serializers.DecimalField(
        max_digits=2,
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
            score = Decimal(str(value))
            if not score.as_tuple().exponent >= -1:  # Ensure only one decimal place
                raise serializers.ValidationError("Score must have at most one decimal place.")
            if score < Decimal('0.0') or score > Decimal('5.0'):
                raise serializers.ValidationError("Score must be between 0 and 5.")
            return score
        except (InvalidOperation, TypeError):
            raise serializers.ValidationError("Invalid score format. Must be a decimal number.")

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        rating = super().create(validated_data)
        rating.movie.update_rating()
        return rating

    def update(self, instance, validated_data):
        rating = super().update(instance, validated_data)
        rating.movie.update_rating()
        return rating 