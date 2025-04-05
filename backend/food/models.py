from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models

from food.constants import MAX_LENGTH_FIELD_STR, MAX_LENGTH_TITLE


UNIT_CHOICES = [
    ("кг", "кг"),
    ("г", "г"),
    ("л", "л"),
    ("мл", "мл"),
]


class CookUser(AbstractUser):
    email = models.EmailField(unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'password',
        'first_name',
        'last_name',
        'username'
    ]
    
    avatar = models.ImageField(
        'Аватар',
        upload_to='avatars/',
        null=True,
        blank=True
        # default = "foodgram/frontend/src/images/userpic-icon.jpg"
    )
    
    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ["username"]

    def __str__(self):
        return self.username


User = get_user_model()


class Ingredient(models.Model):
    title = models.CharField(
        'Название ингридиента',
        max_length=MAX_LENGTH_TITLE)
    unit = models.CharField(
        'Единица измерения',
        max_length=MAX_LENGTH_TITLE,
        choices=UNIT_CHOICES)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.title[:MAX_LENGTH_FIELD_STR]


class Tag (models.Model):
    title = models.CharField(
        'Название тега',
        max_length=MAX_LENGTH_TITLE)
    slug = models.SlugField('Слаг', unique=True)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.title


class Recipe(models.Model):
    '''Модель рецепта.'''

    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(
        'Название рецепта',
        max_length=MAX_LENGTH_TITLE)
    image = models.ImageField(
        'Изображение рецепта',
        upload_to='dishes/',
        null=True,
        blank=True
    )
    text = models.TextField('Описание рецепта')
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True
    )

    ingredients = models.ManyToManyField(Ingredient, "Ингридиенты")

    tags = models.ManyToManyField(Tag, "Тэги")

    cook_time = models.IntegerField()

    def clean(self):
        if self.cook_time < 0:
            raise ValidationError(
                "Время приготовления не может быть меньше 1 минуты")
        elif self.cook_time > 1440:
            raise ValidationError(
                "Время приготовления не может быть больше 24 часов.")

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        default_related_name = 'recipes'
        ordering = ["-pub_date"]

    def __str__(self):
        return self.title[:MAX_LENGTH_FIELD_STR]
