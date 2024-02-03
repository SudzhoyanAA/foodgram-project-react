from django.contrib.auth import get_user_model

from rest_framework import mixins, status, viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from djoser.views import UserViewSet

from api.utils.permissoins import IsAdminAuthorOrReadOnly
from .serializers import (
    UserSignUpSerializer, UserSubscribeSerializer, UserSubscribeReadSerializer
)


User = get_user_model()


class CustomUserViewSet(UserViewSet):
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

    def create(self, request, *args, **kwargs):
        serializer = UserSignUpSerializer(
            data=request.data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    # @action(
    #     detail=False, methods=['get'],
    #     serializer_class=UserSubscribeReadSerializer,
    #     url_path='subscriptions', url_name='subscriptions'
    # )
    # def subscriptions(self, request):
    #     subscriptions = User.objects.filter(following__user=request.user)
    #     serializer = UserSubscribeReadSerializer(subscriptions, many=True)
    #     return Response(serializer.data)

# Вообщем эта проблема осталась не решенной.
# Причем даже ошибок в логах нет, просто путсая белая страница.


class UserSubscriptionsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """Получения всех подписок на пользователя."""

    serializer_class = UserSubscribeReadSerializer

    def get_queryset(self):
        return User.objects.filter(following__user=self.request.user)
