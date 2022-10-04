from django.contrib import admin

from .models import (IngredientInRecipe, Ingredients, IsFavorite,
                     IsInShoppingCart, IsSubscribed, Recipes, Tags)


class RecipesAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'favorite',)
    list_filter = ('name', 'author', 'tags',)

    def favorite(self, obj):
        if IsFavorite.objects.filter(recipe=obj).exists():
            return IsFavorite.objects.filter(recipe=obj).count()
        return 0


class IngredientInRecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    list_filter = ('name',)
    search_fields = ('name',)


admin.site.register(Recipes, RecipesAdmin)
admin.site.register(Ingredients, IngredientInRecipeAdmin)
admin.site.register(Tags)
admin.site.register(IngredientInRecipe)
admin.site.register(IsFavorite)
admin.site.register(IsSubscribed)
admin.site.register(IsInShoppingCart)
