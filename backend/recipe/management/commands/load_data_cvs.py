import csv
import logging

from django.core.management.base import BaseCommand
from recipe.models import Ingredients, Tag

logger = logging.getLogger(__name__)


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

        tags_file_path = "data/tags.csv"
        with open(tags_file_path, "r", encoding="utf-8") as file:
            reader = csv.reader(file, delimiter=",")
            tags_to_create = []
            for row in reader:
                name, color, slug = map(str.strip, row)
                if name:
                    tag = Tag(name=name, color=color, slug=slug)
                    tags_to_create.append(tag)
            Tag.objects.bulk_create(tags_to_create)
