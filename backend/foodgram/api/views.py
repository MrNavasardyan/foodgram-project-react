from django.db.models import Sum
from django.http.response import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
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
    RecipeItemSerializer
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

    @action(detail=False, methods=['GET'],
            pagination_class=None,
            permission_classes=(IsAuthenticated,))
    def me(self, request):
        serializer = CustomUserSerializer(request.user)
        return Response(serializer.data,
                        status=status.HTTP_200_OK)

    @action(
        detail=False, methods=['GET'],
        permission_classes=(IsAuthenticated,),
        url_path='subscriptions',
    )
    def subscriptions(self, request):
        user = request.user
        queryset = Follow.objects.filter(user=user)
        page = self.paginate_queryset(queryset)
        serializer = FollowSerializer(page, many=True,
                                      context={'request': request})
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
                            'Нельзя подписаться на самого себя.'
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
        elif request.method == 'DELETE':
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
    def post_favorite(model, user, recipe):
        model_create, create = model.objects.get_or_create(
            user=user, recipe=recipe
        )
        if create:
            if str(model) == 'Favorite':
                serializer = FavoriteSerializer()
            return Response(
                serializer.to_representation(instance=model_create),
                status=status.HTTP_201_CREATED,
            )

    @staticmethod
    def delete_favorite(model, user, recipe):
        model.objects.filter(user=user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


    def get_serializer_class(self):
        if self.action in ('retrieve', 'list'):
            return RecipeListSerializer
        return RecipeCreateSerializer


    @action(detail=True, methods=['POST', 'DELETE'],
            permission_classes=(IsAuthenticated,))
    def favorite(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)

        if request.method == 'POST':
            if Favorite.objects.filter(user=user, recipe=recipe).exists():
                return Response(
                    {'favorite': 'Рецепт уже добавлен в избранное.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return self.post_favorite(Favorite, user, recipe)
        elif request.method == 'DELETE':
            return self.delete_favorite(
                Favorite, user, recipe
            )
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=('POST', 'DELETE'),
        detail=True,
        permission_classes=(IsAuthenticated,),
    )
    def shopping_cart(self, request, pk):
        """
        Получить / Добавить / Удалить  рецепт
        из списка покупок у текущего пользоватля.
        """
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            serializer = CartSerializer(recipe, data=request.data,
                                        context={"request": request})
            serializer.is_valid(raise_exception=True)
            if not ShoppingCart.objects.filter(user=request.user,
                                               recipe=recipe).exists():
                ShoppingCart.objects.create(user=request.user, recipe=recipe)
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            return Response({'errors': 'Рецепт уже в списке покупок.'},
                            status=status.HTTP_400_BAD_REQUEST)

        elif request.method == 'DELETE':
            cart = ShoppingCart.objects.filter(recipe=recipe)
            if cart.exists():
                cart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['GET'],
            permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request, **kwargs):
        ingredients = (
            RecipeIngredient.objects
            .filter(recipe__cart__user=request.user)
            .values('ingredient')
            .annotate(total_amount=Sum('amount'))
            .values_list('ingredient__name', 'total_amount',
                         'ingredient__measurement_unit')
        )
        file_list = []
        [file_list.append(
            '{} - {} {}.'.format(*ingredient)) for ingredient in ingredients]
        file = HttpResponse('Cписок покупок:\n' + '\n'.join(file_list),
                            content_type='text/plain')
        file['Content-Disposition'] = (f'attachment; filename={dt.now()}')
        return file
