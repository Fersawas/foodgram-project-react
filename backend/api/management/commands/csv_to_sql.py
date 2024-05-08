import csv
import os
from typing import Any

from django.core.management.base import BaseCommand
from food.models import IngredientMesurment, Tag


class Command(BaseCommand):

    def handle(self, *args: Any, **options: Any) -> str | None:
        path = os.path.normpath("data/ingredients.csv")
        with open(path, "r", encoding="utf-8") as file:
            csv_reader = csv.reader(file, delimiter=",")
            objects = [
                IngredientMesurment(name=row[0], measurement_unit=row[1])
                for row in csv_reader
            ]
            IngredientMesurment.objects.bulk_create(objects)

        path = os.path.normpath("data/tags.csv")
        with open(path, "r", encoding="utf-8") as file:
            csv_reader = csv.reader(file, delimiter=",")
            objects = [
                Tag(name=row[0], slug=row[1],
                    color=row[2]) for row in csv_reader
            ]
            Tag.objects.bulk_create(objects)
