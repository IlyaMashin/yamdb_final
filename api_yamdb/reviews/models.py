from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .validators import validate_username, validate_year

USER = 'user'
MODERATOR = 'moderator'
ADMIN = 'admin'

CHOICES = (
    (USER, 'Пользователь'),
    (MODERATOR, 'Модератор'),
    (ADMIN, 'Админ'),
)

USERNAME_LENGTH = 150
FIRST_NAME_LENGTH = 150
LAST_NAME_LENGTH = 150
EMAIL_LENGTH = 254
CONFIRMATION_CODE_LENGTH = 6


class ReviewCommentBase(models.Model):
    text = models.TextField(
        verbose_name='текст'
    )
    author = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name='%(class)ss',
        verbose_name='автор',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='дата создания',
    )

    class Meta:
        abstract = True
        ordering = ('-pub_date',)

    def __str__(self):
        return f'{self.text[:20]}, {self.author}, {self.pub_date}'


class User(AbstractUser):
    username = models.CharField(
        verbose_name='Пользователь',
        max_length=USERNAME_LENGTH,
        unique=True,
        validators=[validate_username]
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=FIRST_NAME_LENGTH,
        blank=True,
        null=True,
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=LAST_NAME_LENGTH,
        blank=True,
        null=True,
    )
    bio = models.TextField(
        blank=True,
        verbose_name='Биография'
    )
    role = models.CharField(
        max_length=max(len(role) for role, _ in CHOICES),
        choices=CHOICES,
        default=USER,
        verbose_name='Роль'
    )
    email = models.EmailField(
        max_length=EMAIL_LENGTH, unique=True, verbose_name='Почта'
    )
    confirmation_code = models.CharField(
        'Код подтверждения',
        max_length=CONFIRMATION_CODE_LENGTH,
        blank=True
    )

    REQUIRED_FIELDS = ['email']

    @property
    def is_admin(self):
        return self.role == ADMIN or self.is_staff

    @property
    def is_moderator(self):
        return self.role == MODERATOR

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class CategoryGenreBase(models.Model):
    name = models.CharField(
        unique=True,
        max_length=256,
        verbose_name='Именование',
        blank=False
    )
    slug = models.SlugField(
        unique=True,
        max_length=50,
        verbose_name='Слаг',
        blank=False
    )

    class Meta:
        abstract = True
        ordering = ('name',)

    def __str__(self):
        return self.name


class Categories(CategoryGenreBase):

    class Meta(CategoryGenreBase.Meta):
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Genre(CategoryGenreBase):

    class Meta(CategoryGenreBase.Meta):
        verbose_name = 'Жанр',
        verbose_name_plural = 'Жанры'


class Title(models.Model):
    name = models.TextField(
        verbose_name='Название произведения',
    )
    year = models.IntegerField(
        verbose_name='Год',
        validators=[validate_year],
        null=True,
    )
    genre = models.ManyToManyField(
        Genre,
        related_name='titles',
        verbose_name='genre_titles'
    )
    category = models.ForeignKey(
        Categories,
        blank=True,
        null=True,
        related_name='titles',
        on_delete=models.SET_NULL,
        verbose_name='Категория'
    )

    description = models.TextField(
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        ordering = ('name',)

    def __str__(self):
        return f'Произведение: {self.name}'


class Review(ReviewCommentBase):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='произведение',
    )
    score = models.IntegerField(
        validators=(
            MinValueValidator(1),
            MaxValueValidator(10)
        ),
        verbose_name='оценка',
    )

    class Meta(ReviewCommentBase.Meta):
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [models.UniqueConstraint(
            fields=('title', 'author'),
            name='unique_review'
        )]


class Comment(ReviewCommentBase):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='отзыв'
    )

    class Meta(ReviewCommentBase.Meta):
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
