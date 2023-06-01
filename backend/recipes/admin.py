from django.contrib import admin

from .models import (Follow, Ingredient, IngredientRecipe,
                     Recipe, Tag,)


class IngredientsInline(admin.TabularInline):
    '''
    Админка добавления ингридиентов в рецепты.
    Сразу доступно добавление 3х ингрдиентов.
    '''
    model = IngredientRecipe
    extra = 3


class FollowAdmin(admin.ModelAdmin):
    '''
    Админка подписок.
    '''
    list_display = ('user', 'author')
    list_filter = ('author',)
    search_fields = ('user',)


class IngredientRecipeAdmin(admin.ModelAdmin):
    '''
    Админка ингридентов для рецептов.
    '''
    list_display = ('id', 'recipe', 'ingredient', 'amount',)
    list_filter = ('recipe', 'ingredient')
    search_fields = ('name',)


class RecipeAdmin(admin.ModelAdmin):
    '''
    Админка рецептов.
    '''
    list_display = ('id', 'author', 'name', 'pub_date', 'in_favorite', )
    search_fields = ('name',)
    list_filter = ('pub_date', 'author', 'name', 'tags')
    filter_horizontal = ('ingridients',)
    empty_value_display = '-пусто-'
    inlines = [IngredientsInline]


class TagAdmin(admin.ModelAdmin):
    '''
    Админка тегов.
    '''
    list_display = ('id', 'name', 'slug', 'color')
    list_filter = ('name',)
    search_fields = ('name',)


class IngredientAdmin(admin.ModelAdmin):
    '''
    Админка ингридиентов.
    '''
    list_display = ('name', 'measurement')
    list_filter = ('name',)
    search_fields = ('name',)


admin.site.register(Recipe)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag)
admin.site.register(IngredientRecipe)
admin.site.register(Follow)
