from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator

from foodgram.constants import (
    LENGHT_150, LENGHT_254, LENGHT_200,
    MIN_VALUE, MIN_VALUE_MSG, LENGHT_7,
)
from .validators import username_validator, color_validator


class User(AbstractUser):
    username = models.CharField(
        verbose_name='Имя пользователя',
        max_length=LENGHT_150,
        unique=True,
        validators=[username_validator],
    )
    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        max_length=LENGHT_254,
        unique=True,
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=LENGHT_150
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=LENGHT_150
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['username']

    def __str__(self):
        return self.username


class Ingredients(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=LENGHT_200,
        unique=True
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=LENGHT_200,
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['name']

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Тег',
        max_length=LENGHT_200,
        unique=True
    )
    slug = models.SlugField(
        verbose_name='Слаг',
        max_length=LENGHT_200,
        unique=True,
        db_index=True,
    )
    color = models.CharField(
        verbose_name='Цвет',
        max_length=LENGHT_7,
        unique=True,
        validators=[color_validator]
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ['name']

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='recipes'
    )
    name = models.CharField(
        verbose_name='Название',
        max_length=LENGHT_200,
    )
    image = models.ImageField(
        verbose_name='Изображение',
        upload_to='recipe/image'
    )
    text = models.TextField(
        verbose_name='Описание'
    )
    ingredients = models.ManyToManyField(
        Ingredients,
        verbose_name='Ингредиенты',
        related_name='recipes',
        through="RecipeIngredient",
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
        related_name='recipes'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=[MinValueValidator(MIN_VALUE, MIN_VALUE_MSG)],
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-id']

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
    )
    ingredient = models.ForeignKey(
        Ingredients,
        verbose_name='Ингридиент',
        on_delete=models.CASCADE,
        related_name='recipe_ingredients'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Колличество',
        validators=[MinValueValidator(MIN_VALUE, MIN_VALUE_MSG)],
    )

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'
        db_table = 'recipes_recipe_ingredient'
        ordering = ['id']

    def __str__(self):
        return (
            f'{self.recipe.name}: '
            f'{self.ingredient.name} - '
            f'{self.amount}/'
            f'{self.ingredient.measurement_unit}'
        )


class Subscribe(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Подписчик',
        on_delete=models.CASCADE,
        related_name='follower'
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='following'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = ['author']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_user_author',
            )
        ]

    def __str__(self):
        return f'{self.user} подписчик автора - {self.author}'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='favorites'
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='favorites'
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        ordering = ['id']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_user_favorite',
            )
        ]

    def __str__(self):
        return f'{self.user} - {self.recipe}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='carts'
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='carts'
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        db_table = 'recipes_shopping_cart'
        ordering = ['id']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_user_cart',
            )
        ]

    def __str__(self):
        return f'{self.user} - {self.recipe}'
