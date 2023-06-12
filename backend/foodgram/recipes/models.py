from django.core import validators
from django.db import models

from users.models import CustomUser


class Tag(models.Model):
    """Модель тега."""

    ORANGE = '#E26C2D'
    GREEN = '#49B64E'
    PURPLE = '#8775D2'

    HEX_CHOICES = [
        ('#E26C2D', ORANGE),
        ('#49B64E', GREEN),
        ('#8775D2', PURPLE),
    ]

    name = models.CharField(
        'Название',
        max_length=200,
        unique=True,
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        validators=[
            validators.RegexValidator(
                regex=r'^[-a-zA-Z0-9_]+$',
                message='Недопустимое значение поля.',
            )
        ],
    )
    color = models.CharField(
        'Цветовой HEX-код',
        max_length=7,
        unique=True,
        choices=HEX_CHOICES,
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель ингредиента."""

    name = models.CharField(
        'Название ингредиента',
        max_length=200,
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=200,
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='distinct_measurement',
            )
        ]

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецепта."""

    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор',
        db_index=True,
    )
    name = models.CharField(
        'Название рецепта',
        max_length=200,
    )
    image = models.ImageField(
        'Фото',
        upload_to='recipe_images/',
        blank=True,
    )
    text = models.TextField('Описание')
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='recipes',
        verbose_name='Ингредиенты',
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Тег',
        db_index=True,
    )
    cooking_time = models.PositiveIntegerField('Время приготовления')

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    """Модель ингредиента рецепта."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredient',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipe_ingredient',
    )
    amount = models.PositiveSmallIntegerField(
        validators=(
            validators.MinValueValidator(
                1,
                message=(
                    'Нельзя просто так взять и приготовить рецепт '
                    'без ингредиентов.'
                ),
            ),
        ),
        verbose_name='Количество',
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецепта'
        constraints = [
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='distinct_ingredients',
            )
        ]

    def __str__(self):
        return f'Ингредиент {self.ingredient} для рецепта {self.recipe}'


class Favorite(models.Model):
    """Модель списка избранного."""

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт',
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Любимый рецепт'
        verbose_name_plural = 'Избранное'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='distinct_favorite',
            )
        ]

    def __str__(self):
        return f'{self.user} {self.recipe}'


class ShoppingCart(models.Model):
    """Модель списка покупок."""

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='cart',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='cart',
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='distinct_cart',
            )
        ]

    def __str__(self):
        return f'{self.user} {self.recipe}'
