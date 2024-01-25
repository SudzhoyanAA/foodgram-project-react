from django.contrib.auth import get_user_model
from django.forms import ValidationError

from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from djoser.serializers import UserCreateSerializer, UserSerializer

from api.utils.check_functions import check_subscribe
from recipe.models import Favorite, Recipe, ShoppingCart, Subscribe

User = get_user_model()


class UserGetSerializer(UserSerializer):
    """Получение информации о пользователе."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        return check_subscribe(self.context.get('request'), obj)


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


class RecipeShortSerializer(serializers.ModelSerializer):
    """Краткая информация о рецепте."""

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class FavoriteSerializer(serializers.ModelSerializer):
    """Избранные рецепты."""

    class Meta:
        model = Favorite
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=model.objects.all(),
                fields=['user', 'recipe'],
                message='Рецепт уже добавлен в избранное.',
            )
        ]

    def to_representation(self, instance):
        request = self.context.get('request')
        return RecipeShortSerializer(
            instance.recipe, context={'request': request}
        ).data


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
