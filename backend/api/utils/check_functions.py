from django.db import transaction

from recipe.models import Ingredients, RecipeIngredient


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
    with transaction.atomic():
        RecipeIngredient.objects.bulk_create(
            RecipeIngredient(
                recipe=recipe,
                ingredient=Ingredients.objects.get(id=ingredient.get('id')),
                amount=ingredient.get('amount'),
            )
            for ingredient in ingredients
        )
