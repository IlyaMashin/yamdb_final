from django.core.mail import send_mail
from django.db import IntegrityError
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django.utils.crypto import get_random_string
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.tokens import RefreshToken
from reviews.models import (CONFIRMATION_CODE_LENGTH, Categories, Genre,
                            Review, Title, User)

from api_yamdb.settings import DEFAULT_EMAIL

from .filters import TitleFilter
from .permissions import (AdminOnlyAccess, AdminOrModeratorOrAuthorOrReadOnly,
                          AdminOrReadOnly)
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, GetTokenSerializer,
                          ReviewSerializer, SignUpSerializer,
                          TitleCreateSerializer, TitleSerializer,
                          UserSerializer)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def signup(request):
    serializer = SignUpSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    try:
        user, _ = User.objects.get_or_create(
            email=serializer.validated_data.get('email'),
            username=serializer.validated_data.get('username'),
        )
    except IntegrityError:
        return Response(
            'Этот email или username уже существует',
            status=status.HTTP_400_BAD_REQUEST
        )
    user.confirmation_code = get_random_string(length=CONFIRMATION_CODE_LENGTH)
    user.save()
    send_mail(
        subject="Регистрационный код",
        message=f"Ваш код подтверждения: {user.confirmation_code}",
        from_email=DEFAULT_EMAIL,
        recipient_list=[user.email, ],
    )

    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def get_token(request):
    serializer = GetTokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = get_object_or_404(
        User,
        username=serializer.validated_data.get('username')
    )
    if (
        (user.confirmation_code
            == serializer.validated_data.get('confirmation_code'))
        and user.confirmation_code
    ):
        return Response(
            {'token': str(RefreshToken.for_user(user).access_token)},
            status=status.HTTP_200_OK
        )
    user.confirmation_code = ''
    user.save()
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryGenreParentViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    permission_classes = (AdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    lookup_field = 'slug'
    search_fields = ('name',)


class CategoryViewSet(CategoryGenreParentViewSet):
    queryset = Categories.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(CategoryGenreParentViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')
    ).all()
    serializer_class = TitleSerializer
    pagination_class = PageNumberPagination
    permission_classes = (AdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    ordering_fields = ('name', 'year', 'genre', 'category')

    def get_serializer_class(self):
        if self.request.method not in permissions.SAFE_METHODS:
            return TitleCreateSerializer
        return TitleSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = PageNumberPagination
    permission_classes = (AdminOnlyAccess, )
    filter_backends = (filters.SearchFilter, )
    filterset_fields = ('username')
    search_fields = ('=username', )
    lookup_field = "username"

    @action(detail=False, methods=['get', 'patch'],
            permission_classes=(IsAuthenticated, ))
    def me(self, request):
        user = self.request.user
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = self.get_serializer(user,
                                         data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(role=user.role)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    pagination_class = PageNumberPagination
    permission_classes = (AdminOrModeratorOrAuthorOrReadOnly, )

    def get_title(self):
        return get_object_or_404(Title, pk=self.kwargs.get('title_id'),)

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title())


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    pagination_class = PageNumberPagination
    permission_classes = (AdminOrModeratorOrAuthorOrReadOnly, )

    def get_review(self):
        return get_object_or_404(Review, pk=self.kwargs.get('review_id'))

    def get_queryset(self):
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())
