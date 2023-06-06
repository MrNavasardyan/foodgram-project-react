import os
from django.conf import settings
from django.db.models import Sum
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

    @action(
        methods=('GET',),
        detail=False,
        permission_classes=(IsAuthenticated,),
    )
    def download_shopping_cart(self, request):
        user = request.user
        ingredients = (
            RecipeIngredient.objects.filter(recipe__shoppingcart__user=user)
            .values(
                'ingredient__name',
                'ingredient__measurement_unit',
            )
            .annotate(ingredient_sum=Sum('amount'))
            .values_list(
                'ingredient__name',
                'ingredient_sum',
                'ingredient__measurement_unit',
            )
        )
        response_list = {}
        for item in ingredients:
            name = item[0]
            if name not in response_list:
                response_list[name] = {
                    'amount': item[1],
                    'measurement_unit': item[2],
                }
            else:
                response_list[name]['amount'] += item[2]
        pdfmetrics.registerFont(
            ttfonts.TTFont(
                'AGHelveticaCyr',
                os.path.join(settings.BASE_DIR, 'fonts', 'AGHelveticaCyr.ttf'),
                'UTF-8',
            )
        )
        response = HttpResponse(content_type='application/pdf')
        shopping_cart_list = canvas.Canvas(response)
        shopping_cart_list.setFont('AGHelveticaCyr', size=24)
        shopping_cart_list.drawString(200, 770, 'Cписок покупок')
        shopping_cart_list.setFont('AGHelveticaCyr', size=14)
        height = 700
        for list_number, (name, data) in enumerate(response_list.items(), 1):
            shopping_cart_list.drawString(
                80,
                height,
                (
                    f'{list_number}. {name} - {data["amount"]} '
                    f'{data["measurement_unit"]}'
                ),
            )
            height -= 20
        shopping_cart_list.showPage()
        shopping_cart_list.save()
        return response