from django_filters.rest_framework import filters, FilterSet

from food.models import Recipe, Tag, IngredientMesurment


class IngredientsFilter(FilterSet):
    name = filters.CharFilter(lookup_expr='startswith')

    class Meta:
        model = IngredientMesurment
        fields = ['name', ]


class RecipeFilter(FilterSet):
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(method='filter_shopcart')
    tags = filters.ModelMultipleChoiceFilter(
        to_field_name='slug',
        field_name='tags__slug',
        queryset=Tag.objects.all(),
    )

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if value and not user.is_anonymous:
            return queryset.filter(favorite__user=user)
        return queryset

    def filter_shopcart(self, queryset, name, value):
        user = self.request.user
        if value and not user.is_anonymous:
            return queryset.filter(shopcart__user=user)
        return queryset

    class Meta:
        model = Recipe
        fields = (
            'author',
            'tags'
        )
