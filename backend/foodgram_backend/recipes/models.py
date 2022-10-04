
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class Ingredients(models.Model):
    """Модель ингредиентов."""
    name = models.CharField('Наименование продукта', max_length=64)
    measurement_unit = models.CharField('Единица измерений', max_length=10)

    class Meta:
        ordering = ['name']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Tags(models.Model):
    """Модель тэгов."""
    name = models.CharField(max_length=50,
                            unique=True,
                            verbose_name='Название'
                            )
    color = models.CharField(max_length=10,
                             unique=True,
                             verbose_name='Цветовой HEX-код',
                             blank=True,
                             null=True,
                             default='FF'
                             )
    slug = models.SlugField(max_length=50, unique=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return f'{self.name}'


class Recipes(models.Model):
    """Модель рецептов."""
    name = models.CharField(max_length=16)
    tags = models.ManyToManyField(Tags, related_name='recipes',
                                  verbose_name='теги')
    author = models.ForeignKey(User, related_name='recipes',
                               on_delete=models.CASCADE)
    ingredients = models.ManyToManyField(Ingredients,
                                         related_name='recipes',
                                         verbose_name='Ингредиенты',
                                         through='IngredientInRecipe')
    image = models.ImageField(upload_to='recipes/images/',
                              null=True, default=None, blank=True)
    text = models.TextField(verbose_name='Описание')
    cooking_time = models.PositiveIntegerField(
        default=1, validators=[MinValueValidator(1, message='минимум 1')],
        verbose_name='Время готовности'
        )
    date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class IngredientInRecipe(models.Model):
    """Модель колличества ингредиентов в рецепте."""
    ingredient = models.ForeignKey(Ingredients,
                                   related_name='ingredient',
                                   on_delete=models.PROTECT)
    recipe = models.ForeignKey(Recipes, related_name='recipe',
                               on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(
        default=1, validators=[MinValueValidator(1, message='минимум 1')]
    )

    class Meta:
        ordering = ['ingredient']
        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количество ингредиентов'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_ingredient'
                )
            ]

    def __str__(self):
        return (
            f'{self.recipe}  {self.ingredient},'
            f'количество = {self.amount}'
        )


class IsFavorite(models.Model):
    """Модель избранных рецептов."""
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='favorite',
                             verbose_name='Пользователь')
    recipe = models.ForeignKey(Recipes,
                               on_delete=models.CASCADE,
                               related_name='favorite',
                               verbose_name='Рецепт')

    class Meta:
        ordering = ['-id']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_user_recipe'
            )
        ]
        verbose_name_plural = 'Избранные'

    def __str__(self):
        return f'{self.user} {self.recipe}'


class IsSubscribed(models.Model):
    """Модель подписки на авторов рецептов."""
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='following',
                               verbose_name='Автор')
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='follower',
                             verbose_name='Подписчик')
    created = models.DateTimeField('Дата подписки', auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Подписки'
        ordering = ['-id']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_user_author'
            )
        ]

    def __str__(self):
        return f'{self.user} подписан {self.author}'


class IsInShoppingCart(models.Model):
    """Модель для добавления ингредиентов в список покупок."""
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='shopping_carts',
                             verbose_name='Пользователь')
    recipe = models.ForeignKey(Recipes,
                               on_delete=models.CASCADE,
                               related_name='shopping_carts',
                               verbose_name='Рецепт')

    class Meta:
        ordering = ['-id']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_recipes_in_shopping_cart'
            )
        ]
        verbose_name_plural = 'Список покупок'

    def __str__(self):
        return f'{self.user} {self.recipe}'
