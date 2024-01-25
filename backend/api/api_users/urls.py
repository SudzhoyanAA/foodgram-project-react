from django.urls import path, include

from rest_framework.routers import DefaultRouter

from .views import CustomUserViewSet, UserSubscriptionsViewSet

router = DefaultRouter()

router.register(r'users', CustomUserViewSet, basename='users')

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
]
