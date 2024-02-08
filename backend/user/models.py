from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError

from foodgram.constants import (
    MAX_NAME_LENGTH, MAX_EMAIL_LENGHT
)
from recipe.validators import username_validator

# Если что сайт работает, но видимо что-то с виртуальной машиной,
# потому что контейнеры запускаются работают, а потом отключаются.


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


class Subscribe(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Подписчик',
        on_delete=models.CASCADE,
        related_name='follower',
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

    def clean(self):
        if self.user == self.author:
            raise ValidationError('Нельзя подписываться на самого себя.')

    def __str__(self):
        return f'{self.user} подписчик автора - {self.author}'
