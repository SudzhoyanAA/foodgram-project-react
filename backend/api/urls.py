from django.urls import path, include

from rest_framework.routers import DefaultRouter

from .views import (
    CustomDjoserUserViewSet, IngredientsViewSet,
    RecipeViewSet, TagViewSet, UserSubscribeView,
    UserSubscriptionsViewSet
)

router = DefaultRouter()

router.register(r'recipes', RecipeViewSet, basename='recipes')
router.register(r'ingredients', IngredientsViewSet, basename='ingredients')
router.register(r'users', CustomDjoserUserViewSet, basename='users')
router.register(r'tags', TagViewSet, basename='tags')


urlpatterns = [
    path(
        'users/subscriptions/',
        UserSubscriptionsViewSet.as_view({'get': 'list'}),
    ),
    path(
        'users/<int:user_id>/subscribe/',
        UserSubscribeView.as_view(),
    ),
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
