import csv

from django.core.management.base import BaseCommand
from recipes.models import Ingredients, Tags


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write('Загрузка данных')
        with open(
            './data/ingredients.csv', encoding='utf-8',
                newline='') as file:
            reader = csv.reader(file)
            for row in reader:
                name, unit = row
                Ingredients.objects.get_or_create(
                    name=name,
                    measurement_unit=unit)
            self.stdout.write('Ингредиенты успешно внесены в базу')
        with open('./data/tags.csv', encoding='utf-8', newline='') as file:
            reader = csv.reader(file)
            for row in reader:
                name, color, slug = row
                Tags.objects.get_or_create(
                    name=name,
                    color=color,
                    slug=slug)
            self.stdout.write('Теги успешно внесены в базу')
