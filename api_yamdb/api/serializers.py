from rest_framework import serializers
from reviews.models import (CONFIRMATION_CODE_LENGTH, EMAIL_LENGTH,
                            USERNAME_LENGTH, Categories, Comment, Genre,
                            Review, Title, User)
from reviews.validators import validate_year

from .validators import UserValidator


class SignUpSerializer(serializers.Serializer, UserValidator):
    username = serializers.CharField(max_length=USERNAME_LENGTH)
    email = serializers.EmailField(max_length=EMAIL_LENGTH)


class GetTokenSerializer(serializers.Serializer, UserValidator):
    username = serializers.CharField(max_length=USERNAME_LENGTH)
    confirmation_code = serializers.CharField(
        max_length=CONFIRMATION_CODE_LENGTH
    )


class UserSerializer(serializers.ModelSerializer, UserValidator):

    class Meta:
        model = User
        fields = (
            'username', 'first_name', 'last_name', 'email', 'role', 'bio'
        )


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Categories
        exclude = ('id',)


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        exclude = ('id',)


class TitleSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    genre = GenreSerializer(many=True)
    rating = serializers.IntegerField()

    class Meta:
        model = Title
        fields = (
            'id', 'category', 'genre', 'name',
            'year', 'rating', 'description',
        )
        read_only_fields = fields


class TitleCreateSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        many=True,
    )
    category = serializers.SlugRelatedField(
        queryset=Categories.objects.all(),
        slug_field='slug',
    )
    year = serializers.IntegerField(validators=[validate_year])

    class Meta:
        model = Title
        fields = ('name', 'year', 'description', 'genre', 'category', 'id')


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )
    score = serializers.IntegerField(max_value=10, min_value=1)

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')

    def validate(self, data):
        if self.context['request'].method != 'POST':
            return data
        user = self.context['request'].user
        title_id = self.context['view'].kwargs.get('title_id')
        if Review.objects.filter(author=user, title_id=title_id):
            raise serializers.ValidationError(
                'Нельзя оставлять больше одного отзыва!'
            )
        return data


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
