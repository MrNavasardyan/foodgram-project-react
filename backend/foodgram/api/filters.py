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
        method='is_favorited'
    )

    is_in_shopping_cart = filters.BooleanFilter(
        field_name='is_in_shopping_cart', method='is_in_shopping_cart')

    tags = filters.ModelMultipleChoiceFilter(field_name='tags__slug',
                                             to_field_name='slug',
                                             queryset=Tag.objects.all())

    def is_favorited(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return Recipe.objects.filter(favorites__user=self.request.user)
        return queryset


    def is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return Recipe.objects.filter(cart__user=self.request.user)
        return queryset

    class Meta:
        model = Recipe
        fields = ('tags', 'author',)



    # class Meta:
    #     model = Recipe
    #     fields = ('tags', 'author',)

