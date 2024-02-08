from django.urls import path, include

from rest_framework.routers import DefaultRouter

from .views import CustomUserViewSet

router = DefaultRouter()

router.register(r'users', CustomUserViewSet, basename='users')

urlpatterns = [
    path(
        'users/subscriptions/',
        CustomUserViewSet.as_view({'get': 'subscriptions'}),
    ),
    path(
        'users/<int:user_id>/subscribe/',
        CustomUserViewSet.as_view(
            {'post': 'subscribe', 'delete': 'unsubscribe'}
        ),
    ),
    path('', include(router.urls)),
]
