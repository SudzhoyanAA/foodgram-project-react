import base64

from django.core.files.base import ContentFile

from rest_framework import serializers

from recipe.models import Ingredients, RecipeIngredient


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


def check_subscribe(request, author):
    return (
        request.user.is_authenticated
        and request.user.follower.filter(author=author).exists()
    )


def check_recipe(request, obj, model):
    return (
        request
        and request.user.is_authenticated
        and model.objects.filter(user=request.user, recipe=obj).exists()
    )


def add_ingredients(ingredients, recipe):
    ingredient_list = [
        RecipeIngredient(
            recipe=recipe,
            ingredient=Ingredients.objects.get(id=ingredient.get('id')),
            amount=ingredient.get('amount'),
        )
        for ingredient in ingredients
    ]
    RecipeIngredient.objects.bulk_create(ingredient_list)
