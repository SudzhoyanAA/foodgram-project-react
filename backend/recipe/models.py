from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models

from foodgram.constants import (
    MAX_NAME_LENGTH, MAX_EMAIL_LENGHT, MAX_FIELD_LENGTH,
    MIN_VALUE, MIN_VALUE_MSG, MAX_COLOR_LENGHT, MAX_INFO_LENGTH
)
from .validators import color_validator, username_validator

# Вообщем по поводу разделение проекта полностью и избавлением директории api.
# При разделение логики именно моделей, сыпется БД и возникают
# какие то странные ошибки. Просидел несколько дней исправляя их,
# в итоге уперся
# В одну ошибку связанную с приватным ключом при добавлении
# ингредиентов в рецепты.
# Поэтому сделал так и отправляю так, писал в пачку тебе,
# но понимаю, что я не один.
# Вижу ожин выхож, если все таки нужно разделить и модели,
# это полностью начинать заново.


class User(AbstractUser):
    REQUIRED_FIELDS = ('username', 'password')
    USERNAME_FIELD = ('email')

    username = models.CharField(
        verbose_name='Имя пользователя',
        max_length=MAX_NAME_LENGTH,
        unique=True,
        validators=[username_validator],
    )
    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        max_length=MAX_EMAIL_LENGHT,
        unique=True,
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=MAX_NAME_LENGTH
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=MAX_NAME_LENGTH
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['username']


class Ingredients(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=MAX_FIELD_LENGTH,
        unique=True
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=MAX_FIELD_LENGTH,
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
        max_length=MAX_FIELD_LENGTH,
        unique=True
    )
    slug = models.SlugField(
        verbose_name='Слаг',
        max_length=MAX_FIELD_LENGTH,
        unique=True,
        db_index=True,
    )
    color = models.CharField(
        verbose_name='Цвет',
        max_length=MAX_COLOR_LENGHT,
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
        max_length=MAX_FIELD_LENGTH,
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

# Тут создается строка автор - рецепт и возвращается подстрока с ограничением.
    def __str__(self):
        info_string = f'{self.author} - {self.name}'
        return info_string[:MAX_INFO_LENGTH]


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
                condition=models.Q(user=models.F('author')),
            )
        ]

# думал через метод clean сделать, но ты вроде в 12 спринте говорил,
# что так лучше не делать.
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
