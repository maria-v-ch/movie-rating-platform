from rest_framework import serializers
from django.contrib.auth import get_user_model
from movies.serializers import MovieSerializer

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    favorite_movies = MovieSerializer(many=True, read_only=True)
    total_reviews = serializers.IntegerField(read_only=True)
    average_rating_given = serializers.FloatField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'date_joined',
            'favorite_movies', 'total_reviews',
            'average_rating_given'
        ]
        read_only_fields = ['date_joined']

class UserCreateSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2']
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Passwords must match.")
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'bio', 'profile_image']
        read_only_fields = ['username']

    def validate_email(self, value):
        user = self.context['request'].user
        if User.objects.exclude(pk=user.pk).filter(email=value).exists():
            raise serializers.ValidationError("This email is already in use.")
        return value 