from django_filters import rest_framework as filters

from recipes.models import Ingredient, Recipe


class IngredientLookupFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(filters.FilterSet):
    """Фильтр рецептов по тегам, избранному, списку покупок."""

    is_favorite = filters.BooleanFilter(
        field_name='is_favorite', method='favorite_filter'
    )
    is_cart = filters.BooleanFilter(field_name='is_cart', method='cart_filter')
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')

    def favorite_filter(self, queryset, name, value):
        recipes = Recipe.objects.filter(favorites__author=self.request.user)
        return recipes

    def cart_filter(self, queryset, name, value):
        recipes = Recipe.objects.filter(cart__author=self.request.user)
        return recipes

    class Meta:
        model = Recipe
        fields = ('author',)
