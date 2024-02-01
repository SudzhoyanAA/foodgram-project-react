from django.forms import ValidationError

from rest_framework import serializers

from api.api_users.serializers import UserGetSerializer
from api.utils.check_functions import add_ingredients, check_recipe
from api.utils.serializers import Base64ImageField
from foodgram.constants import MIN_VALUE, MAX_VALUE
from recipe.models import (
    Ingredients, Recipe, RecipeIngredient,
    Favorite, Tag, ShoppingCart
)


class IngredientsSerializer(serializers.ModelSerializer):
    """Ингредиенты."""

    class Meta:
        model = Ingredients
        fields = '__all__'


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Ингредиенты в рецепте."""

    name = serializers.SlugRelatedField(
        slug_field='name',
        read_only=True,
        source='ingredient',
    )
    measurement_unit = serializers.SlugRelatedField(
        slug_field='measurement_unit',
        read_only=True,
        source='ingredient',
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )


class TagSerializer(serializers.ModelSerializer):
    """Тэг."""

    class Meta:
        model = Tag
        fields = '__all__'


class RecipeGetSerializer(serializers.ModelSerializer):
    """Получение информации о рецепте."""

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
    """Добавление ингредиентов в рецепт."""
# id нужен для строчки 157.
    id = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')

    def validate_amount(self, value):
        if MIN_VALUE <= value <= MAX_VALUE:
            return value
        raise serializers.ValidationError("Недопустимое значение для amount.")


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    """Создание рецептов."""

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
        instance.ingredients.clear()
        super().update(instance, validated_data)
        add_ingredients(ingredients, instance)
        return instance

    def to_representation(self, instance):
        return RecipeGetSerializer(instance, context=self.context).data

# Тут я не совсем понял, делаю метод приватным через _ и падают тесты.
    def validate_tags(self, tags):
        if len(set(tags)) != len(tags):
            raise ValidationError('Теги должны быть уникальными!')
        return tags


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
