from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from djoser.views import UserViewSet

from api.utils.permissoins import IsAdminAuthorOrReadOnly
from .serializers import (
    UserSignUpSerializer, UserSubscribeSerializer, UserSubscribeReadSerializer,
)


User = get_user_model()


class CustomUserViewSet(UserViewSet):
    """Костомный пользователь."""
    permission_classes = (IsAdminAuthorOrReadOnly,)

    def get_permissions(self):
        if self.action == 'me':
            return [IsAuthenticated()]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == 'create':
            return UserSignUpSerializer
        return super().get_serializer_class()

    @action(detail=True, methods=['post'], url_path='subscribe')
    def subscribe(self, request, user_id=None):
        author = get_object_or_404(User, id=user_id)
        serializer = UserSubscribeSerializer(
            data={'user': request.user.id, 'author': author.id},
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['delete'], url_path='unsubscribe')
    def unsubscribe(self, request, user_id=None):
        author = get_object_or_404(User, id=user_id)
        follower = request.user.follower.filter(author=author)
        if not follower:
            return Response(
                {'error': 'Нет подписки на этого пользователя'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        follower.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True, methods=['get'], url_path='subscriptions',
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request, *args, **kwargs):
        queryset = User.objects.filter(following__user=self.request.user)
        serializer = UserSubscribeReadSerializer(
            queryset, many=True, context={"request": request}
        )
        return Response({'results': serializer.data})
