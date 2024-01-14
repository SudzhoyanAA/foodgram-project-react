from django.db.models import Sum
from django.http import HttpResponse

from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from recipe.models import Recipe, RecipeIngredient


class RecipeFunctions:
    @staticmethod
    def add_recipe(serializer_name, request, recipe):
        serializer = serializer_name(
            data={'user': request.user.id, 'recipe': recipe.id},
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @staticmethod
    def delete_recipe(model, request, err_msg, recipe):
        obj = model.objects.filter(user=request.user, recipe=recipe)
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'error': err_msg}, status=status.HTTP_400_BAD_REQUEST)

    def execute(self, serializer_name, model, request, pk, err_msg):
        if request.method == 'POST':
            try:
                recipe = Recipe.objects.get(id=pk)
            except Recipe.DoesNotExist:
                raise ValidationError(
                    'Рецепт с указанным идентификатором не существует.'
                )
            return self.add_recipe(serializer_name, request, recipe)

        if request.method == 'DELETE':
            recipe = get_object_or_404(Recipe, id=pk)
            return self.delete_recipe(model, request, err_msg, recipe)


def get_shopping_cart(request):
    user = request.user
    if not user.carts.exists():
        return Response(
            {'error': 'Корзины пользователя не найдены.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    ingredients = (
        RecipeIngredient.objects.filter(recipe__carts__user=request.user)
        .values(
            'ingredient__name',
            'ingredient__measurement_unit',
        )
        .annotate(ingredient_amount=Sum('amount'))
    )
    shopping_list = f'Список покупок пользователя {user}:\n'

    for ingredient in ingredients:
        name = ingredient['ingredient__name']
        unit = ingredient['ingredient__measurement_unit']
        amount = ingredient['ingredient_amount']
        shopping_list += f"\n{name} - {amount}/{unit}"

    file_name = f'{user}_shopping_cart.txt'
    response = HttpResponse(shopping_list, content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename={file_name}'
    return response
