from django.contrib.auth import get_user_model
from djoser.views import UserViewSet as DjoserUserViewSet

from rest_framework import mixins, status, viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.utils.permissoins import IsAdminAuthorOrReadOnly
from .serializers import UserSubscribeReadSerializer, UserSubscribeSerializer


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


class UserSubscriptionsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """Получения всех подписок на пользователя."""

    serializer_class = UserSubscribeReadSerializer

    def get_queryset(self):
        return User.objects.filter(following__user=self.request.user)
