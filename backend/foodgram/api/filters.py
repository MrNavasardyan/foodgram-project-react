from django_filters import rest_framework as filters

from recipes.models import Ingredient, Recipe, Tag
from users.models import CustomUser


class IngredientLookupFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(filters.FilterSet):
    """Фильтр рецептов по тегам, избранному, списку покупок."""
    author = filters.ModelChoiceFilter(
        queryset=CustomUser.objects.all())

    is_favorited = filters.BooleanFilter(
        method='is_favorited', label='favorite', field_name='is_favorite'
    )

    is_in_shopping_cart = filters.BooleanFilter(field_name='is_cart',
                                                label='shoppings_list',
                                                method='is_in_shopping_cart')

    tags = filters.ModelMultipleChoiceFilter(field_name='tags__slug',
                                             to_field_name='slug',
                                             queryset=Tag.objects.all())

    class Meta:
        model = Recipe
        fields = ('author', 'tags',)

    def is_favorited(self, queryset, name, value):
        if value and self.request and self.request.user.is_authenticated:
            return queryset.filter(favorites__user=self.request.user)
        return queryset.exclude(favorites__user=self.request.user)

    def is_in_shopping_cart(self, queryset, name, value):
        if value and self.request and self.request.user.is_authenticated:
            return Recipe.objects.filter(cart__user=self.request.user)
        return queryset
