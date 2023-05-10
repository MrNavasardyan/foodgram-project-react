from django.core.exceptions import ValidationError
from users.models import User


def validate_email(value):
    if User.objects.filter(email=value).exists():
        raise ValidationError(
            {'email уже существует'},
        )
    return value