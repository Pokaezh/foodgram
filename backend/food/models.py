from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.core.validators import MinValueValidator


from food.constants import MAX_LENGTH_FIELD_STR, MAX_LENGTH_TITLE


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
        blank=True,
    )

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ["username"]

    def __str__(self):
        return self.username[:MAX_LENGTH_FIELD_STR]


User = get_user_model()


class Follow(models.Model):
    '''Модель для подписок.'''

    user = models.ForeignKey(
        User,
        related_name='following',
        on_delete=models.CASCADE,
        blank=True, null=True)
    following = models.ForeignKey(
        User,
        related_name='followers',
        on_delete=models.CASCADE,
        blank=True, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'following'], name='unique_follow'),
        ]

    def __str__(self):
        return f'{self.user.username} follows {self.following.username}'


class Ingredient(models.Model):
    name = models.CharField(
        'Название ингридиента',
        max_length=MAX_LENGTH_TITLE)
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=MAX_LENGTH_TITLE,)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=("name", "measurement_unit",),
                name="unique_ingredient_unit",
            ),
        ]

    def __str__(self):
        return self.name[:MAX_LENGTH_FIELD_STR]


class Tag (models.Model):
    name = models.CharField(
        'Название тега',
        max_length=MAX_LENGTH_TITLE)
    slug = models.SlugField('Слаг', unique=True)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    '''Модель рецепта.'''

    author = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(
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

    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='recipes')

    tags = models.ManyToManyField(Tag, related_name='recipes')

    cooking_time = models.IntegerField()

    short_link = models.CharField(
        "Хеш для короткой ссылки",
        max_length=6,
        unique=True,
        null=True,
        blank=True,
    )

    def clean(self):
        if self.cooking_time < 0:
            raise ValidationError(
                "Время приготовления не может быть меньше 1 минуты")
        elif self.cooking_time > 1440:
            raise ValidationError(
                "Время приготовления не может быть больше 24 часов.")

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        default_related_name = 'recipes'
        ordering = ["-pub_date"]

    def __str__(self):
        return self.name[:MAX_LENGTH_FIELD_STR]


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipeingredients',
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipeingredients',
        verbose_name='Ингредиент'
    )
    amount = models.PositiveIntegerField(
        'Количество',
        validators=[
            MinValueValidator(
                1, 'Количество ингредиентов не может быть меньше 1')
        ]
    )

    class Meta:
        unique_together = ('recipe', 'ingredient')
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт',
    )

    class Meta:
        ordering = ['-id']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_user_recipe_favorite'
            )
        ]
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'


class ShoppingCart(models.Model):
    """Модель списка покупок """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_user',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_recipe',
        verbose_name='Рецепт'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_shoppingcart'
            )
        ]

    def __str__(self):
        return f'{self.user} {self.recipe}'
