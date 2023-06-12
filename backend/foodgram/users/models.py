from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin)
from django.core import validators
from django.db import models


class CustomUserManager(BaseUserManager):
    """Модель управления пользователями."""

    def create_user(self, email, username, password, **extra_fields):
        if not email:
            raise ValueError('Поле email необходимо заполнить.')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, username, password, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_superuser'):
            return self.create_user(email, username, password, **extra_fields)
        raise ValueError('Для пользователя не настроены права администратора.')


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """Модель авторизации."""

    username = models.CharField(
        'Логин',
        max_length=150,
        unique=True,
        blank=False,
        validators=[
            validators.RegexValidator(
                regex=r'^[\w.@+-]{3,150}$',
                message='Недопустимое значение поля.',
            )
        ],
    )
    password = models.CharField(
        'Пароль',
        max_length=150,
        blank=False,
    )
    email = models.EmailField(
        'Email',
        max_length=254,
        unique=True,
        blank=False,
        validators=[
            validators.EmailValidator(message='Недопустимое значение поля.')
        ],
    )
    first_name = models.CharField(
        'Имя',
        max_length=150,
        blank=False,
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=150,
        blank=False,
    )
    is_superuser = models.BooleanField(
        'Администратор',
        default=False,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'username',
        'first_name',
        'last_name',
        'password',
    ]

    objects = CustomUserManager()

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username

    @property
    def is_staff(self):
        return self.is_superuser


class Follow(models.Model):
    """Модель подписки."""

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
        null=True,
    )
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор',
        null=True,
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='distinct_follow',
            )
        ]

    def __str__(self):
        return f'{self.user} подписан на {self.author}'
