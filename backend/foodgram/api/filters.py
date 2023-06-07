from django_filters import rest_framework as filters

from recipes.models import Ingredient, Recipe
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
        field_name='favorite', method='is_favorited'
    )

    is_in_shopping_cart = filters.BooleanFilter(
        field_name='is_in_shopping_cart', method='is_in_shopping_cart')

    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')

    def is_favorited(self, queryset, name, value):
        recipes = Recipe.objects.filter(favorites__user=self.request.user)
        return recipes

    def is_in_shopping_cart(self, queryset, name, value):
        recipes = Recipe.objects.filter(cart__user=self.request.user)
        return recipes

    class Meta:
        model = Recipe
        fields = ('author',)
