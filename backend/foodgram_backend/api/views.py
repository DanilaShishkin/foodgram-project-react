from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from recipes.models import (IngredientInRecipe, Ingredients, IsFavorite,
                            IsInShoppingCart, IsSubscribed, Recipes, Tags,
                            User)
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import SAFE_METHODS, AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT

from .filters import IngredientsSearchFilter, RecipesFilter
from .permissions import IsAuthorOrReadOnly
from .serializers import (FollowSerializer, IngredientsSerializer,
                          IsFavoriteSerializer, IsInShoppingSerializer,
                          IsSubscribedSerializer, RecipeCreateSerializer,
                          RecipesSerializer, TagsSerializer)


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipes.objects.all()
    permission_classes = [IsAuthorOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipesFilter
    pagination_class = PageNumberPagination

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipesSerializer
        return RecipeCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['POST'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk):
        data = {'user': request.user.id, 'recipe': pk}
        serializer = IsFavoriteSerializer(data=data,
                                          context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=HTTP_201_CREATED)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipes, id=pk)
        favorite = get_object_or_404(IsFavorite, user=user, recipe=recipe)
        favorite.delete()
        return Response(status=HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['POST'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk):
        data = {'user': request.user.id, 'recipe': pk}
        serializer = IsInShoppingSerializer(data=data,
                                            context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=HTTP_201_CREATED)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipes, id=pk)
        user = request.user
        shopping_list = get_object_or_404(IsInShoppingCart,
                                          user=user,
                                          recipe=recipe)
        shopping_list.delete()
        return Response(status=HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'],
            url_path='download_shopping_cart',
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request, pk=None):
        ingredients = IngredientInRecipe.objects.filter(
            recipe__shopping_carts__user=request.user.id
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount'))
        shopping_cart = ['Список покупок:\n--------------']
        for position, ingredient in enumerate(ingredients, start=1):
            shopping_cart.append(
                f'\n{position}. {ingredient["ingredient__name"]}:'
                f' {ingredient["amount"]}'
                f'({ingredient["ingredient__measurement_unit"]})'
            )
        response = FileResponse(shopping_cart, as_attachment=True,
                                content_type='text')
        response['Content-Disposition'] = (
            'attachment;filename=in_shopping_cart.txt'
        )
        return response


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer
    pagination_class = None
    permission_classes = (AllowAny, )
    filter_backends = [IngredientsSearchFilter]
    search_fields = ('^name',)


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tags.objects.all()
    serializer_class = TagsSerializer
    pagination_class = None
    permission_classes = (AllowAny,)


class UserSubscribeViewSet(UserViewSet):
    pagination_class = PageNumberPagination

    @action(detail=False, permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        user = request.user
        queryset = IsSubscribed.objects.filter(user=user)
        pages = self.paginate_queryset(queryset)
        serializer = FollowSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['POST'],
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, id):
        user = request.user
        author = get_object_or_404(User, id=id)
        subscribe = IsSubscribed.objects.create(user=user, author=author)
        serializer = IsSubscribedSerializer(
            subscribe, context={'request': request}
        )
        return Response(serializer.data, status=HTTP_201_CREATED)

    @subscribe.mapping.delete
    def delete_subscribe(self, request, id):
        user = request.user
        author = get_object_or_404(User, id=id)
        subscribed = IsSubscribed.objects.filter(user=user, author=author)
        if subscribed.exists():
            subscribed.delete()
        return Response(status=HTTP_204_NO_CONTENT)
