from django.db.models import Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from api.utils.filters import IngredientFilter, RecipeFilter
from api.utils.permissoins import IsAdminAuthorOrReadOnly
from api.users.serializers import ShoppingCartSerializer, FavoriteSerializer
from recipe.models import (
    Ingredients, Recipe, RecipeIngredient, Favorite, Tag, ShoppingCart
)
from .serializers import (
    IngredientsSerializer, RecipeCreateUpdateSerializer,
    RecipeGetSerializer, TagSerializer
)


class RecipeViewSet(viewsets.ModelViewSet):
    """Рецепт."""
    queryset = Recipe.objects.all()
    permission_classes = (IsAdminAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeGetSerializer
        return RecipeCreateUpdateSerializer

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated],
    )
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        serializer = FavoriteSerializer(
            data={'user': request.user.id, 'recipe': recipe.id},
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        obj = Favorite.objects.filter(user=request.user, recipe=recipe)
        err_msg = 'Рецепт отсутствует в избранном.'

        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'error': err_msg}, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated],
    )
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        serializer = ShoppingCartSerializer(
            data={'user': request.user.id, 'recipe': recipe.id},
            context={'request': request},
        )
        err_msg = 'Рецепт отсутствует в списке покупок.'

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {'error': err_msg}, status=status.HTTP_400_BAD_REQUEST
            )

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        obj = ShoppingCart.objects.filter(user=request.user, recipe=recipe)

        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            err_msg = 'Рецепт отсутствует в списке покупок.'
            return Response(
                {'error': err_msg}, status=status.HTTP_400_BAD_REQUEST
            )

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated],
    )
    def download_shopping_cart(self, request):
        user = request.user

        if not user.carts.exists():
            return Response(
                {'error': 'Корзины пользователя не найдены.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        user_recipes = Recipe.objects.filter(favorites__user=user)
        ingredients = RecipeIngredient.objects.filter(recipe__in=user_recipes)
        shopping_list = self.generate_shopping_list(ingredients)
        file_name = f'{user}_shopping_cart.txt'
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={file_name}'
        return response

    def generate_shopping_list(self, ingredients):
        aggregated_ingredients = ingredients.values(
            'ingredient__name',
            'ingredient__measurement_unit',
        ).annotate(ingredient_amount=Sum('amount'))

        shopping_list = 'Список покупок:\n'

        for ingredient in aggregated_ingredients:
            name = ingredient['ingredient__name']
            unit = ingredient['ingredient__measurement_unit']
            amount = ingredient['ingredient_amount']
            shopping_list += f"\n{name} - {amount}/{unit}"

        return shopping_list


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    """Ингридиенты."""
    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Тэг."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
