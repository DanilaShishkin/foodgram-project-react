from django_filters.rest_framework import FilterSet, filters
from rest_framework.filters import SearchFilter

from recipes.models import Recipes


class RecipesFilter(FilterSet):
    """Фильтр рецептов."""
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')
    is_favorited = filters.BooleanFilter(method='favorite')
    is_in_shopping_cart = filters.BooleanFilter(method='shopping_cart')

    class Meta:
        model = Recipes
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart')

    def favorite(self, queryset, name, value):
        if value:
            return queryset.filter(favorite__user=self.request.user)
        return queryset

    def shopping_cart(self, queryset, name, value):
        if value:
            return queryset.filter(shopping_carts__user=self.request.user)
        return queryset


class IngredientsSearchFilter(SearchFilter):
    """Фильтр игредиентов."""
    search_param = 'name'
