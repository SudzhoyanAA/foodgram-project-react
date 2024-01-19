from django.contrib.auth import get_user_model
from rest_framework import serializers

from djoser.serializers import UserSerializer

from api.utils.check_functions import check_subscribe

User = get_user_model()


class UserGetSerializer(UserSerializer):
    """Получение информации о пользователе."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        return check_subscribe(self.context.get('request'), obj)
