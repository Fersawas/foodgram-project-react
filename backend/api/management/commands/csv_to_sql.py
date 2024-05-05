import csv
import os
from typing import Any
from food.models import Tag, IngredientMesurment
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def handle(self, *args: Any, **options: Any) -> str | None:
        path = os.path.normpath('data/ingredients.csv')
        with open(path, 'r', encoding='utf-8') as file:
            csv_reader = csv.reader(file, delimiter=',')
            for row in csv_reader:
                print(row)
                IngredientMesurment.objects.create(
                    name=row[0], measurement_unit=row[1])

        path = os.path.normpath('data/tags.csv')
        with open(path, 'r', encoding='utf-8') as file:
            csv_reader = csv.reader(file, delimiter=',')
            for row in csv_reader:
                print(row)
                Tag.objects.create(
                    name=row[0], slug=row[1], color=row[2]
                )
