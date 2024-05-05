from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator, EmailValidator

from .constants import MAX_EMAIL_LENGTH, MAX_LENGTH


class UserMain(AbstractUser):
    username = models.CharField(
        verbose_name='Логин',
        max_length=MAX_LENGTH,
        validators=(
            RegexValidator(r'[\w@+-]+'),
        ),
        unique=True
    )
    email = models.EmailField(
        max_length=MAX_EMAIL_LENGTH,
        unique=True,
        validators=(
            EmailValidator(
                message='Incorrect email'),
        ))
    first_name = models.CharField(
        max_length=MAX_LENGTH,
        blank=False,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=MAX_LENGTH,
        blank=False,
        verbose_name='Фамилия'
    )
    password = models.CharField(
        max_length=MAX_LENGTH,
        verbose_name='Пароль'
    )

    class Meta:
        verbose_name: str = 'Пользователь'
        verbose_name_plural: str = 'Пользователи'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', ]


User = get_user_model()


class Follow(models.Model):
    user = models.ForeignKey(
        User, related_name='main',
        on_delete=models.CASCADE,
        verbose_name='На кого подписаны'
    )
    follower = models.ForeignKey(
        User, related_name='follows',
        on_delete=models.CASCADE,
        verbose_name='Подписчик'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'follower'],
                name='unique-follows'
            )
        ]
        verbose_name: str = 'Подписка'
        verbose_name_plural: str = 'Подписки'

    def __str__(self) -> str:
        return str(self.user)
