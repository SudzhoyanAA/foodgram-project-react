from django.contrib.auth import get_user_model
from django.forms import ValidationError
from djoser.serializers import UserCreateSerializer

from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from recipe.models import (
    Subscribe, ShoppingCart
)
from .api_users.serializers import UserGetSerializer
from .api_recipes.serializers import RecipeShortSerializer


User = get_user_model()


class UserSignUpSerializer(UserCreateSerializer):
    """Создание пользователя."""

    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'password',
        )


class UserSubscribeReadSerializer(UserGetSerializer):
    """Получение информации о подписке."""

    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )
        read_only_fields = (
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = None
        if request:
            recipes_limit = request.query_params.get('recipes_limit')
        recipes = obj.recipes.all()
        if recipes_limit:
            recipes = obj.recipes.all()[: int(recipes_limit)]
        return RecipeShortSerializer(
            recipes, many=True, context={'request': request}
        ).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class UserSubscribeSerializer(serializers.ModelSerializer):
    """Подписка"""
    class Meta:
        model = Subscribe
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=Subscribe.objects.all(),
                fields=('user', 'author'),
                message='Вы уже подписаны на этого пользователя',
            )
        ]

    def validate_author(self, value):
        request = self.context.get('request')
        if request.user == value:
            raise ValidationError('Нельзя подписаться на самого себя!')
        return value

    def to_representation(self, instance):
        request = self.context.get('request')
        return UserSubscribeReadSerializer(
            instance.author, context={'request': request}
        ).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Список покупок."""

    class Meta:
        model = ShoppingCart
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=model.objects.all(),
                fields=['user', 'recipe'],
                message='Рецепт уже добавлен в список покупок.',
            )
        ]
