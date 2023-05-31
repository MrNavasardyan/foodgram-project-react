from django.core.validators import RegexValidator
from rest_framework.validators import UniqueValidator
from djoser.serializers import UserSerializer, TokenCreateSerializer
from users.models import User
from rest_framework import serializers
from users.validators import validate_email


class CustomUserCreateSerializer(UserSerializer):
    email = serializers.EmailField(
        max_length=254, allow_blank=False, validators=[validate_email]
    )
    username = serializers.CharField(
        max_length=150,
        allow_blank=False,
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+\Z', message='Введите корректный username'
            ),
            UniqueValidator(queryset=User.objects.all()),
        ],
    )
    first_name = serializers.CharField(max_length=150, required=True)
    last_name = serializers.CharField(max_length=150, required=True)
    password = serializers.CharField(max_length=150, required=True)

    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'password')

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class CustomTokenCreateSerializer(TokenCreateSerializer):
    email = serializers.EmailField(
        max_length=254, required=True
    )
    password = serializers.CharField(
        required=True, style={
            "input_type": "password"})

    class Meta:
        model = User
        fields = ('email', 'password')
