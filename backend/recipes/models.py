from django.db import models
from django.core.validators import MinValueValidator
from users.models import User
from .tags_color import TagsColor

class Tag(models.Model):
    """Модель тегов для рецептов."""

    name = models.CharField(
        verbose_name='Название тега',
        max_length=200, unique=True,
        help_text='Введите название тега')

    color = models.CharField(
        verbose_name='Цвета в HEX-color',
        max_length=7, unique=True,
        default=TagsColor.CHOCOLATE,
        choices=TagsColor.TAGS,
        help_text='Выбрать цвет')

    slug = models.SlugField(
        verbose_name='Слаг',
        max_length=200, unique=True,
        help_text='Укажите уникальный слаг')

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingridient(models.Model):
    """Модель для ингридентов"""
    name = models.CharField(
        verbose_name='Название ингредиента',
        max_length=200,
        db_index=True,
        help_text='Введите название ингредиента')

    measurement = models.CharField(
        verbose_name='Единица измерения',
        max_length=200,
        help_text='Введите единицу измерения')

    class Meta:
        ordering = ['id']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name}'



class Recipe(models.model):
    "Модель рецептов"

    author = models.ForeignKey(
        User,
        verbose_name='Автор рецепта',
        on_delete=models.CASCADE,
        help_text='Автор рецепта')

    name = models.CharField(
        verbose_name='Название рецепта',
        max_length=200,
        help_text='Введите название рецепта',
        db_index=True)

    image = models.ImageField(
        verbose_name='Изображение рецепта',
        upload_to='media/',
        help_text='Добавьте изображение рецепта')

    ingridients = models.ManyToManyField(
        Ingridient,
        through='IngredientRecipe',
        verbose_name='Ингредиент')

    tags = models.ManyToManyField(
        Tag,
        verbose_name='Название тега',
        help_text='Выберите tag')

    cook_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=[MinValueValidator(1, 'Минимальное время приготовления')],
        help_text='Укажите время приготовления рецепта в минутах')


    class Meta:
        ordering = ['-id']
        default_related_name = 'recipe'
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'author'],
                name='unique_recipe')]


class Follow(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='follower'
    )
    following = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='following'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'following'], name='unique follow'
            ),
        ]

    def __str__(self):
        return f'Пользователь {self.user} подписан на {self.author}'
