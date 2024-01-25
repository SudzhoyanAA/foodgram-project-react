from django.db.models import Sum
from django.http import HttpResponse

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from api.utils.filters import IngredientFilter, RecipeFilter
from api.utils.permissoins import IsAdminAuthorOrReadOnly
from api.utils.utils_views import RecipeFunctions
from recipe.models import (
    Ingredients, Recipe, RecipeIngredient, ShoppingCart, Favorite, Tag
)
from api.api_users.serializers import (
    ShoppingCartSerializer, FavoriteSerializer
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
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated],
    )
    def favorite(self, request, pk):
        recipe_func = RecipeFunctions()
        err_msg = 'Рецепт отсутствует в избранном.'
        return recipe_func.execute(
            FavoriteSerializer, Favorite, request, pk, err_msg
        )

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated],
    )
    def shopping_cart(self, request, pk):
        recipe_func = RecipeFunctions()
        err_msg = 'Рецепт отсутствует в списке покупок.'
        return recipe_func.execute(
            ShoppingCartSerializer, ShoppingCart, request, pk, err_msg
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

        shopping_list = self.generate_shopping_list(request.user)

        file_name = f'{user}_shopping_cart.txt'
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={file_name}'
        return response

    def generate_shopping_list(self, user):
        ingredients = (
            RecipeIngredient.objects.filter(recipe__carts__user=user)
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
