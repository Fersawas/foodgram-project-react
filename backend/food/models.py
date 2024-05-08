# isort: off
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from api.messages_constants import (COLOR_LENGTH, COOK_VALIDATOR_MESSAGE,
                                    MAX_LENGTH)

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        max_length=MAX_LENGTH,
        verbose_name='Название'
    )
    slug = models.SlugField(
        max_length=MAX_LENGTH,
        verbose_name='Слаг'
    )
    color = models.CharField(
        max_length=COLOR_LENGTH,
        verbose_name='Цвет'
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class IngredientMesurment(models.Model):
    name = models.CharField(
        max_length=MAX_LENGTH,
        verbose_name='Название'
    )
    measurement_unit = models.CharField(
        max_length=MAX_LENGTH,
        verbose_name='Единица измерения'
    )

    class Meta:
        verbose_name = 'Ингредиент/Мера'
        verbose_name_plural = 'Ингредиенты/Меры'

    def __str__(self):
        return self.name


class IngredientCount(models.Model):
    ingredient = models.ForeignKey(
        IngredientMesurment,
        related_name='ingr_count',
        on_delete=models.CASCADE,
        verbose_name='Ингредиенты'
    )
    amount = models.IntegerField(verbose_name='Количество')

    class Meta:
        verbose_name = 'Количество ингредиентов'
        verbose_name_plural = 'Количество ингредиентов'
        constraints = [
            models.UniqueConstraint(
                fields=['ingredient', 'amount'],
                name='ingred-amount'
            )
        ]

    def __str__(self):
        result = (self.ingredient.name + ' '
                  + str(self.amount)
                  + self.ingredient.measurment_unit)
        return result


class Recipe(models.Model):
    name = models.CharField(
        max_length=MAX_LENGTH,
        verbose_name='Название'
    )
    text = models.TextField(verbose_name='Описание')
    ingredients = models.ManyToManyField(
        IngredientCount,
        related_name='recipes',
        verbose_name='Ингредиенты'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги'
    )
    image = models.ImageField(
        upload_to='media/',
        null=True,
        default=None,
        verbose_name='Картинка'
    )
    cooking_time = models.IntegerField(
        validators=[
            MinValueValidator(
                1,
                message=COOK_VALIDATOR_MESSAGE
            )
        ],
        verbose_name='Время готовки'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite',
        verbose_name='Рецепт'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique-favorite'
            )
        ]
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'

    def __str__(self):
        return str(self.user)


class Shopcart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopcart',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopcart',
        verbose_name='Рецепт'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique-shopcart'
            )
        ]
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзина'
