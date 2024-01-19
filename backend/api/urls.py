from django.urls import path, include

from rest_framework.routers import DefaultRouter

from .views import (
    IngredientsViewSet,
    RecipeViewSet, TagViewSet, CustomUserViewSet,
    UserSubscriptionsViewSet
)

router = DefaultRouter()

router.register(r'recipes', RecipeViewSet, basename='recipes')
router.register(r'ingredients', IngredientsViewSet, basename='ingredients')
router.register(r'users', CustomUserViewSet, basename='users')
router.register(r'tags', TagViewSet, basename='tags')

# Разделял логику и когда дошло до организации урлов
# Тесты почему то падали, хотя локально работало, плюс столкнулся с проблемой
# циклических импортов, хотя так и не понял из-за чего она возникла.
urlpatterns = [
    path(
        'users/subscriptions/',
        UserSubscriptionsViewSet.as_view({'get': 'list'}),
    ),
    path(
        'users/<int:user_id>/subscribe/',
        CustomUserViewSet.as_view({'post': 'post', 'delete': 'delete'}),
    ),
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
