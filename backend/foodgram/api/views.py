import os
from rest_framework.status import HTTP_400_BAD_REQUEST
# from django.db.models import Sum
from django.http.response import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from reportlab.pdfbase import pdfmetrics, ttfonts
from reportlab.pdfgen import canvas
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response
from users.models import CustomUser
from .utils import shopping_cart
from datetime import datetime as dt
from django.http.response import HttpResponse
from recipes.models import (
    ShoppingCart,
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    Tag,
)
from users.models import CustomUser, Follow

from .filters import IngredientLookupFilter, RecipeFilter
from .pagination import CustomPageNumberPagination
from .permissions import AdminOrReadOnly, AuthorOrReadOnly
from .serializers import (
    CartSerializer,
    CustomUserSerializer,
    FavoriteSerializer,
    FollowSerializer,
    IngredientSerializer,
    RecipeCreateSerializer,
    RecipeListSerializer,
    TagSerializer,
)


class CustomUserViewSet(UserViewSet):
    """Представление для обработки запросов к ресурсу пользователей."""

    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = (AllowAny,)

    @action(
        methods=('GET',),
        detail=False,
        permission_classes=(IsAuthenticated,),
        url_path='me',
    )
    def get_current_user(self, request):
        user = request.user
        serializer = CustomUserSerializer(
            user,
            context={'request': request},
        )
        if user.is_anonymous:
            return Response(
                {'users': 'Учетные данные не были предоставлены.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    @action(
        methods=('GET',),
        detail=False,
        permission_classes=(IsAuthenticated,),
        url_path='subscriptions',
    )
    def subscriptions(self, request):
        user = request.user
        queryset = Follow.objects.filter(user=user)
        pages = self.paginate_queryset(queryset)
        serializer = FollowSerializer(
            pages,
            many=True,
            context={'request': request},
        )
        return self.get_paginated_response(serializer.data)

    @action(
        methods=('POST', 'DELETE'),
        detail=True,
        permission_classes=(IsAuthenticated,),
    )
    def subscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(CustomUser, id=id)
        if request.method == 'POST':
            if user == author:
                return Response(
                    {
                        'subscribe': (
                            'Нельзя просто так взять и подписаться на себя.'
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            elif Follow.objects.filter(user=user, author=author).exists():
                return Response(
                    {'subscribe': 'Подписка на этого автора уже активна.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            follow = Follow.objects.create(user=user, author=author)
            serializer = FollowSerializer(follow, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        follow = Follow.objects.filter(user=user, author=author)
        if follow.exists():
            follow.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'subscribe': 'Ранее вы уже отписались от этого автора.'},
            status=status.HTTP_400_BAD_REQUEST,
        )


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Представление для обработки запросов к ресурсу тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AdminOrReadOnly,)
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Представление для обработки запросов к ресурсу ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientLookupFilter


class RecipeViewSet(viewsets.ModelViewSet):
    """Представление для обработки запросов к ресурсу рецептов."""

    queryset = Recipe.objects.all()
    permission_classes = (AuthorOrReadOnly,)
    pagination_class = CustomPageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    @staticmethod
    def post_favorite_or_shopping_cart(model, user, recipe):
        model_create, create = model.objects.get_or_create(
            user=user, recipe=recipe
        )
        if create:
            if str(model) == 'Favorite':
                serializer = FavoriteSerializer()
            else:
                serializer = CartSerializer()
            return Response(
                serializer.to_representation(instance=model_create),
                status=status.HTTP_201_CREATED,
            )

    @staticmethod
    def delete_favorite_or_shopping_cart(model, user, recipe):
        model.objects.filter(user=user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_serializer_class(self):
        if self.action in ('retrieve', 'list'):
            return RecipeListSerializer
        return RecipeCreateSerializer

    @action(
        methods=('POST', 'DELETE'),
        detail=True,
        filter_backends=DjangoFilterBackend,
        filterset_class=RecipeFilter,
    )
    def favorite(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            if Favorite.objects.filter(user=user, recipe=recipe).exists():
                return Response(
                    {'favorite': 'Рецепт уже добавлен в избранное.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return self.post_favorite_or_shopping_cart(Favorite, user, recipe)
        elif request.method == 'DELETE':
            return self.delete_favorite_or_shopping_cart(
                Favorite, user, recipe
            )
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=('POST', 'DELETE'),
        detail=True,
        permission_classes=(IsAuthenticated,),
    )
    def shopping_cart(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
                return Response(
                    {'shopping_cart': 'Рецепт уже добавлен в список покупок.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return self.post_favorite_or_shopping_cart(ShoppingCart, user, recipe)
        elif request.method == 'DELETE':
            return self.delete_favorite_or_shopping_cart(ShoppingCart, user, recipe)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(methods=('get',), detail=False)
    def download_shopping_cart(self, request: WSGIRequest) -> Response:
        """Загружает файл *.txt со списком покупок.
        Считает сумму ингредиентов в рецептах выбранных для покупки.
        Возвращает текстовый файл со списком ингредиентов.
        Вызов метода через url:  */recipes/download_shopping_cart/.
        Args:
            request (WSGIRequest): Объект запроса..
        Returns:
            Responce: Ответ с текстовым файлом.
        """
        user = self.request.user
        if not user.carts.exists():
            return Response(status=HTTP_400_BAD_REQUEST)

        filename = f'{user.username}_shopping_list.txt'
        shopping_list = [
            f'Список покупок для:\n\n{user.first_name}\n'
            f'{dt.now()}\n'
        ]

        ingredients = Ingredient.objects.filter(
            recipe__recipe__in_carts__user=user
        ).values(
            'name',
            measurement=F('measurement_unit')
        ).annotate(amount=Sum('recipe__amount'))

        for ing in ingredients:
            shopping_list.append(
                f'{ing["name"]}: {ing["amount"]} {ing["measurement"]}'
            )

        shopping_list.append('\nПосчитано в Foodgram')
        shopping_list = '\n'.join(shopping_list)
        response = HttpResponse(
            shopping_list, content_type='text.txt; charset=utf-8'
        )
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response