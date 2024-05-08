from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from food.models import (Favorite, IngredientCount, IngredientMesurment,
                         Recipe, Shopcart, Tag)
from users.models import Follow, UserMain


@admin.register(UserMain)
class MainUserAdmin(UserAdmin):
    list_display = (
        "username",
        "first_name",
        "last_name",
        "email"
    )
    list_filter = (
        "username",
        "email"
    )


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "color")
    search_fields = ("slug",)


@admin.register(IngredientMesurment)
class IngredientMesureAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "measurement_unit",
    )
    search_fields = ("name",)
    list_filter = ("name", )


@admin.register(IngredientCount)
class IngredCountAdmin(admin.ModelAdmin):
    list_display = (
        "ingredient",
        "amount",
    )
    list_editable = ("amount",)
    list_filter = ("ingredient", )


class IngredInline(admin.StackedInline):
    model = Recipe.ingredients.through
    extra = 0
    verbose_name = 'Ингредиент'
    verbose_name_plural = 'Ингредиенты'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = (IngredInline,)
    list_display = (
        "author",
        "name",
        "text",
        "cooking_time",
        "get_tags",
        "get_ingred",
        "get_favorite")
    exclude = ("ingredients",)

    filter_horizontal = ("tags",)
    search_fields = ("name",)
    list_filter = ("author", "tags")
    list_display_links = ("name",)

    def get_tags(self, obj):
        return [tags.name for tags in obj.tags.all()]

    def get_ingred(self, obj):
        return [
            (f"{ingredients.ingredient.name} - {ingredients.amount}"
             f"{ingredients.ingredient.measurement_unit}")
            for ingredients in obj.ingredients.all()
        ]

    def get_favorite(self, obj):
        numb = Favorite.objects.filter(recipe=obj).count()
        return numb

    get_tags.short_description = "Теги"
    get_ingred.short_description = "Ингредиенты"
    get_favorite.short_description = "Добавлено в избранное"


admin.site.register(Follow)
admin.site.register(Favorite)
admin.site.register(Shopcart)
