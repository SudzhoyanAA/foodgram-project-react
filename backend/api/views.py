from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from django.db.models import Sum
from django.http import HttpResponse

from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from recipe.models import (
    Ingredients, Recipe, RecipeIngredient, ShoppingCart, Favorite, Tag
)
from .serializers import (
    ShoppingCartSerializer,
    UserSubscribeSerializer, UserSubscribeReadSerializer
)
from .api_recipes.serializers import (
    IngredientsSerializer, RecipeCreateUpdateSerializer,
    RecipeGetSerializer, FavoriteSerializer, TagSerializer
)
from .utils.filters import IngredientFilter, RecipeFilter
from .utils.permissoins import IsAdminAuthorOrReadOnly
from .utils.utils_views import RecipeFunctions


User = get_user_model()


class CustomUserViewSet(DjoserUserViewSet, APIView):
    """Костомный пользователь."""

    permission_classes = (IsAdminAuthorOrReadOnly,)

    def get_permissions(self):
        if self.action == 'me':
            return [IsAuthenticated()]
        return super().get_permissions()

    def post(self, request, user_id):
        author = get_object_or_404(User, id=user_id)
        serializer = UserSubscribeSerializer(
            data={'user': request.user.id, 'author': author.id},
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, user_id):
        author = get_object_or_404(User, id=user_id)
        follower = request.user.follower.filter(author=author)
        if not follower:
            return Response(
                {'error': 'Нет подписки на этого пользователя'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        follower.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# У меня не получилось перенести данную вью во вью пользователя ((
# Почему падают тесты, хотя вроде локально работает все,
# поэтому оставил пока что так.


class UserSubscriptionsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """Получения всех подписок на пользователя."""

    serializer_class = UserSubscribeReadSerializer

    def get_queryset(self):
        return User.objects.filter(following__user=self.request.user)


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

# надеюсь я правильно понял, что это замечание могу не трогать так как
# в RecipeFunctions логика удаления и создания разделена.
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
