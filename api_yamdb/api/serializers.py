import datetime

from reviews.models import (Category, Comment, Genre, Review, Title,
                            User)
from django.contrib.auth.validators import UnicodeUsernameValidator
from rest_framework import serializers


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        exclude = ('id',)
        model = Category


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        exclude = ('id',)
        model = Genre


class TitleSerializer(serializers.ModelSerializer):
    """Сериализатор для UNSAFE METHODS"""
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(), slug_field='slug'
    )
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        many=True,
    )
    rating = serializers.IntegerField(read_only=True)

    def validate_year(self, year):
        if year > datetime.datetime.now().year:
            raise serializers.ValidationError('произведение из будущего? нет')
        return year

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description',
                  'rating', 'category', 'genre')


class TitleShowSerializer(serializers.ModelSerializer):
    """Сериализатор для SAFE METHODS"""
    category = CategorySerializer(required=False)
    genre = GenreSerializer(many=True, required=False)
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = Title
        fields = '__all__'


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    def validate(self, data):
        if self.context['request'].method != 'POST':
            return data
        user = self.context['request'].user
        title_id = self.context['view'].kwargs.get('title_id')
        if Review.objects.filter(
            author_id=user.id, title_id=title_id
        ).exists():
            raise serializers.ValidationError(
                'Вы уже оставляли отзыв на данное произведение')
        return data

    class Meta:
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        model = Review


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
    )

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date')
        model = Comment


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор данных для модели User."""

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role',
        )

    def validate(self, data):
        """
        Валидация никнейма.
        Username "me" запрещен.
        """
        username = data.get('username')
        if username == 'me':
            raise serializers.ValidationError(
                'Нельзя использовать "me" в качестве имени пользователя.'
            )
        return data


class RegistrationSerializer(serializers.Serializer):
    """Сериализатор данных при регистрации пользователя."""
    username = serializers.CharField(
        required=True,
        max_length=150,
        validators=[UnicodeUsernameValidator(), ]
    )
    email = serializers.EmailField(
        required=True,
        max_length=254,
    )

    def validate(self, data):
        """
        Валидация полей при регистрации пользователя.
        1) Username "me" запрещен
        2) Неуникальный username запрещен
        3) Неуникальный email запрещен
        """
        username = data.get('username')
        email = data.get('email')
        if username == 'me':
            raise serializers.ValidationError(
                'Нельзя использовать "me" в качестве имени пользователя.'
            )
        if User.objects.filter(username=username, email=email).exists():
            return data
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError(
                'Другой пользователь с таким username уже существует.'
            )
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                'Другой пользователь с таким email уже существует.'
            )
        return data


class EditSelfProfileSerializer(serializers.ModelSerializer):
    """Сериализатор данных при редактировании профиля пользователя."""

    class Meta:
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "bio",
            "role"
        )
        model = User
        read_only_fields = ('role',)

    def validate(self, data):
        """
        Валидация никнейма.
        Username "me" запрещен.
        """
        username = data.get('username')
        if username == 'me':
            raise serializers.ValidationError(
                'Нельзя использовать "me" в качестве имени пользователя.'
            )
        return data


class TokenSerializer(serializers.ModelSerializer):
    """Сериализатор данных при отправке токена."""
    username = serializers.CharField(max_length=100)
    confirmation_code = serializers.CharField(max_length=50)

    class Meta:
        model = User
        fields = ('username', 'confirmation_code')
