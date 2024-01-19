import csv
import logging

from django.core.management.base import BaseCommand
from recipe.models import Ingredients

logger = logging.getLogger(__name__)

# Пробовал локально запускать скрип, работает, но при деплое на сервер
# все ломается, долго просидел над этим, но так и не смог разобраться...
# буду еще пробовать


class Command(BaseCommand):
    def handle(self, *args, **options):
        with open("data/ingredients.csv", "r", encoding="utf-8") as file:
            reader = csv.reader(file, delimiter=",")
            ingredients_to_create = []
            for row in reader:
                name, unit = row
                if name:
                    ingredient = Ingredients(name=name, measurement_unit=unit)
                    ingredients_to_create.append(ingredient)
            Ingredients.objects.bulk_create(ingredients_to_create)
