from django.contrib.auth import get_user_model
from django.forms import ValidationError
from djoser.serializers import UserCreateSerializer, UserSerializer

from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from recipe.models import (
    Ingredients, Recipe, RecipeIngredient,
    Subscribe, Favorite, ShoppingCart, Tag
)
from .utils.utils_serializers import (
    check_subscribe, check_recipe, Base64ImageField, add_ingredients
)
from foodgram.constants import MIN_VALUE, MAX_VALUE


User = get_user_model()


class UserSignUpSerializer(UserCreateSerializer):
    '''Создание пользователя.'''

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


class UserGetSerializer(UserSerializer):
    '''Получение информации о пользователе.'''

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


class UserSubscribeRepresentSerializer(UserGetSerializer):
    '''Получение информации о подписке.'''

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
    '''Подписка'''

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

    def validate(self, data):
        request = self.context.get('request')
        if request.user == data['author']:
            raise ValidationError('Нельзя подписаться на самого себя!')
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        return UserSubscribeRepresentSerializer(
            instance.author, context={'request': request}
        ).data


class IngredientsSerializer(serializers.ModelSerializer):
    '''Ингредиенты.'''

    class Meta:
        model = Ingredients
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    '''Тэг.'''
    class Meta:
        model = Tag
        fields = '__all__'


class RecipeIngredientSerializer(serializers.ModelSerializer):
    '''Ингредиенты в рецепте.'''

    name = serializers.StringRelatedField(
        source='ingredient',
        read_only=True,
    )
    measurement_unit = serializers.StringRelatedField(
        source='ingredient.measurement_unit',
        read_only=True,
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )


class RecipeGetSerializer(serializers.ModelSerializer):
    '''Получение информации о рецепте.'''

    tags = TagSerializer(
        many=True,
        read_only=True,
    )
    author = UserGetSerializer(
        read_only=True,
    )
    ingredients = RecipeIngredientSerializer(
        many=True,
        read_only=True,
        source='recipe_ingredients',
    )
    is_favorited = serializers.SerializerMethodField(
        read_only=True,
    )
    is_in_shopping_cart = serializers.SerializerMethodField(
        read_only=True,
    )

    class Meta:
        model = Recipe
        fields = '__all__'
        extra_fields = ('is_favorited', 'is_in_shopping_cart')

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        return check_recipe(request, obj, Favorite)

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        return check_recipe(request, obj, ShoppingCart)


class IngredientPostSerializer(serializers.ModelSerializer):
    '''Добавление ингредиентов в рецепт.'''

    id = serializers.IntegerField()
    amount = serializers.IntegerField(
        min_value=MIN_VALUE,
        max_value=MAX_VALUE,
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    '''Создание рецептов.'''

    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
    )
    ingredients = IngredientPostSerializer(
        many=True,
        source='recipe_ingredients',
    )
    image = Base64ImageField()
    cooking_time = serializers.IntegerField(
        min_value=MIN_VALUE,
        max_value=MAX_VALUE,
    )

    class Meta:
        model = Recipe
        fields = (
            'tags',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def validate(self, data):
        if not self.initial_data.get('ingredients'):
            raise ValidationError('Рецепт не может быть без ингредиентов.')
        if not self.initial_data.get('tags'):
            raise ValidationError('Рецепт не может быть без тега.')
        return data

    def validate_ingredients(self, ingredients):
        ingredients_list = []
        for item in ingredients:
            try:
                ingredient = Ingredients.objects.get(id=item['id'])
            except Ingredients.DoesNotExist:
                raise ValidationError('Указан несуществующий ингредиент.')

            if ingredient in ingredients_list:
                raise ValidationError('Ингредиенты должны быть уникальными!')

            ingredients_list.append(ingredient)
        return ingredients

    def create(self, validated_data):
        request = self.context.get('request')
        ingredients = validated_data.pop('recipe_ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(author=request.user, **validated_data)
        recipe.tags.set(tags)
        add_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('recipe_ingredients')
        tags = validated_data.pop('tags')
        instance.tags.clear()
        instance.tags.set(tags)
        RecipeIngredient.objects.filter(recipe=instance).delete()
        super().update(instance, validated_data)
        add_ingredients(ingredients, instance)
        instance.save()
        return instance

    def to_representation(self, instance):
        return RecipeGetSerializer(instance, context=self.context).data

    def validate_tags(self, tags):
        if len(set(tags)) != len(tags):
            raise ValidationError('Теги должны быть уникальными!')
        return tags


class RecipeShortSerializer(serializers.ModelSerializer):
    '''Краткая информация о рецепте.'''

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class FavoriteSerializer(serializers.ModelSerializer):
    '''Избранные рецепты.'''

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


class ShoppingCartSerializer(serializers.ModelSerializer):
    '''Список покупок.'''

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
