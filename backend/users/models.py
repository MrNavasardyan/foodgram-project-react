from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from .userroles import UserRoles

from .managers import CustomUserManager

class User(AbstractBaseUser, PermissionsMixin):
    """Пользователи."""
    username = models.CharField('Логин', max_length=150, unique=True)
    first_name = models.CharField('Имя', max_length=150)
    last_name = models.CharField('Фамилия', max_length=150)
    email = models.EmailField(_('email адрес'), unique=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'password', 'first_name', 'last_name']

    objects = CustomUserManager()

    groups = None

    user_permissions = None

    role = models.CharField(
        max_length=100,
        verbose_name='Роль',
        choices=UserRoles.choices,
        default=UserRoles.USER,
    )

    @property
    def is_user(self):
        if self.role == UserRoles.USER:
            return True
        return False

    @property
    def is_admin(self):
        if self.role == UserRoles.ADMIN:
            return True
        return False


    def __str__(self):
        return self.email
