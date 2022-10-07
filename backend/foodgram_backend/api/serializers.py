import webcolors
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.serializers import SerializerMethodField

from recipes.models import (IngredientInRecipe, Ingredients, IsFavorite,
                            IsInShoppingCart, IsSubscribed, Recipes, Tags)
from users.models import User


class Hex2NameColor(serializers.Field):
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        try:
            data = webcolors.hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError('Для этого цвета нет имени')
        return data


class IngredientsSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения списка ингредиентов."""

    class Meta:
        model = Ingredients
        fields = ('id', 'name', 'measurement_unit',)


class IngredientRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения ингредиентов с количеством."""
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount',)


class TagsSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения тэгов."""
    color = Hex2NameColor()

    class Meta:
        model = Tags
        fields = ('id', 'name', 'color', 'slug',)
        read_only_fields = ('id', 'name', 'color', 'slug',)


class UserSerializer(UserCreateSerializer, UserSerializer):
    """Сериализатор для отображения пользователя."""
    is_subscribed = SerializerMethodField(read_only=True)

    class Meta:
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'password', 'is_subscribed',)
        model = User

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        author = get_object_or_404(User, username=obj.username)
        return IsSubscribed.objects.filter(user=request.user.id,
                                           author=author.id).exists()


class AuthorSerializer(serializers.ModelSerializer):
    """Сериализатор для автора."""
    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name',)


class RecipesSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения рецептов."""
    tags = TagsSerializer(many=True, read_only=True)
    author = AuthorSerializer(read_only=True)
    ingredients = IngredientRecipeSerializer(
        source='recipe', required=True, many=True
    )
    image = Base64ImageField(read_only=True, required=False, allow_null=True)
    is_in_shopping_cart = SerializerMethodField()
    is_favorited = SerializerMethodField()

    class Meta:
        fields = ('id', 'tags', 'author',
                  'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image',
                  'text', 'cooking_time',)
        model = Recipes

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return IsInShoppingCart.objects.filter(
            user=request.user, recipe=obj).exists()

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous or (user == obj):
            return False
        return IsFavorite.objects.filter(user=user, recipe=obj).exists()


class IngredientCreateSerializer(serializers.ModelSerializer):
    """Сериализатор создания ингредиентов."""
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = Ingredients
        fields = ('id', 'amount',)


class RecipeCreateSerializer(serializers.ModelSerializer):
    '''Сериализатор создания рецепта'''
    image = Base64ImageField(max_length=None, required=False, use_url=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tags.objects.all()
    )
    ingredients = IngredientCreateSerializer(many=True)

    class Meta:
        model = Recipes
        fields = '__all__'
        read_only_fields = ('author',)

    def validate(self, data):
        if not data['tags']:
            raise serializers.ValidationError(
                'Не выбран тэг.'
            )
        ingredients_list = []
        if not data['ingredients']:
            raise serializers.ValidationError(
                'Не выбран ингредиент'
            )
        for value in data['ingredients']:
            amount = value['amount']
            ingredient = get_object_or_404(Ingredients, id=value['id'])
            if ingredient in ingredients_list:
                raise serializers.ValidationError(
                    'Поле ингредиенты должно быть уникальным'
                )
            if amount < 1:
                raise serializers.ValidationError(
                    'Количество ингредиента должно быть больше 1'
                )
            ingredients_list.append(ingredient)
        if data['cooking_time'] < 1:
            raise serializers.ValidationError(
                'Время приготовления должно быть больше 1 минуты'
            )
        return data

    def create_ingredients(self, ingredient_in_recipe, recipe):
        list_obj = []
        for ingredient in ingredient_in_recipe:
            list_obj.append(
                IngredientInRecipe(
                    recipe=recipe,
                    ingredient_id=ingredient.get('id'),
                    amount=ingredient.get('amount')
                )
            )
        IngredientInRecipe.objects.bulk_create(list_obj)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipes.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        if 'ingredients' in validated_data:
            ingredients = validated_data.pop('ingredients')
            instance.ingredients.clear()
            self.create_ingredients(ingredients, instance)
        if 'tags' in validated_data:
            instance.tags.set(
                validated_data.pop('tags'))
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipesSerializer(
            instance, context={'request': self.context.get('request')}).data


class IsInShoppingSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов в списке покупок."""
    class Meta:
        model = IsInShoppingCart
        fields = ('user', 'recipe',)

    def validate(self, data):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        recipe = data['recipe']
        if IsInShoppingCart.objects.filter(user=request.user,
                                           recipe=recipe).exists():
            raise serializers.ValidationError(
                {'status': 'Ингредиенты уже есть в списке покупок!'}
            )
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipesRepresentSerializer(
            instance.recipe, context=context).data


class RecipesRepresentSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipes
        fields = ('id', 'name', 'image', 'cooking_time',)


class FollowSerializer(serializers.ModelSerializer):
    """Сериализатор рецептов подписанных пользователей."""
    id = serializers.ReadOnlyField(source='author.id')
    email = serializers.ReadOnlyField(source='author.email')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.ReadOnlyField(source='author.recipes.count')

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count',)

    def get_is_subscribed(self, obj):
        return IsSubscribed.objects.filter(
            user=obj.user, author=obj.author
        ).exists()

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        queryset = Recipes.objects.filter(author=obj.author)
        if limit:
            queryset = queryset[:int(limit)]
        return RecipesRepresentSerializer(queryset, many=True).data


class IsSubscribedSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('user', 'author',)
        model = IsSubscribed

    def validate(self, data):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        user = request.user
        author = data['author']
        if user == author:
            raise serializers.ValidationError(
                {'status': 'Нельзя подписываться на себя.'}
            )
        if IsSubscribed.objects.filter(
            user=user,
            author=author
        ).exists():
            raise serializers.ValidationError(
                {'status': 'На этого автора Вы уже подписаны.'}
            )
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return FollowSerializer(
            instance, context=context
        ).data


class IsFavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = IsFavorite
        fields = ('user', 'recipe',)

    def validate(self, data):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        recipe = data['recipe']
        if IsFavorite.objects.filter(user=request.user,
                                     recipe=recipe).exists():
            raise serializers.ValidationError(
                {'status': 'Рецепт уже в избранном.'}
            )
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipesRepresentSerializer(instance.recipe,
                                          context=context).data
