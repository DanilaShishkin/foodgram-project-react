"""Модуль вспомогательных функций.
"""


def create_list_shopping_cart(ingredients):
    shopping_cart = ['Список покупок:\n--------------']
    for position, ingredient in enumerate(ingredients, start=1):
        shopping_cart.append(
            f'\n{position}. {ingredient["ingredient__name"]}:'
            f' {ingredient["amount"]}'
            f'({ingredient["ingredient__measurement_unit"]})'
        )
    return shopping_cart
