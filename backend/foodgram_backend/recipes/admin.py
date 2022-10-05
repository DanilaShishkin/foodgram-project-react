from django.contrib import admin

from .models import (IngredientInRecipe, Ingredients, IsFavorite,
                     IsInShoppingCart, IsSubscribed, Recipes, Tags)


class IngredientInLine(admin.TabularInline):
    model = IngredientInRecipe
    min_num = 1
    extra = 0


class RecipesAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'favorite',)
    list_filter = ('name', 'author__username', 'tags',)
    search_fields = ('name', 'author__username', 'tags__name')
    inlines = (IngredientInLine,)
    empty_value_display = '-пусто-'

    def favorite(self, obj):
        if IsFavorite.objects.filter(recipe=obj).exists():
            return IsFavorite.objects.filter(recipe=obj).count()
        return 0


class IngredientsAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    list_filter = ('name',)
    search_fields = ('name',)
    empty_value_display = '-пусто-'


class IngredientInRecipeAdmin(admin.ModelAdmin):
    list_display = ('ingredient', 'recipe', 'amount')
    list_filter = ('ingredient',)
    search_fields = ('ingredient__name',)
    empty_value_display = '-пусто-'


admin.site.register(Recipes, RecipesAdmin)
admin.site.register(Ingredients, IngredientsAdmin)
admin.site.register(Tags)
admin.site.register(IngredientInRecipe, IngredientInRecipeAdmin)
admin.site.register(IsFavorite)
admin.site.register(IsSubscribed)
admin.site.register(IsInShoppingCart)
