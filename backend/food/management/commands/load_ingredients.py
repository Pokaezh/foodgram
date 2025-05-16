"""Команда для загрузки ингредиентов из JSON файла."""

import json

from django.core.management.base import BaseCommand

from food.models import Ingredient


class Command(BaseCommand):
    """Команда для загрузки ингредиентов из JSON файла."""

    help = 'Load ingredients from JSON file'

    def handle(self, *args, **kwargs):
        """Обрабатывает команду загрузки ингредиентов."""
        added_count = 0  # Счётчик добавленных ингредиентов
        existing_count = 0  # Счётчик существующих ингредиентов

        with open('./data/ingredients.json', encoding='utf-8') as f:
            data = json.load(f)

            for item in data:
                ingredient, created = Ingredient.objects.get_or_create(
                    name=item['name'],
                    measurement_unit=item['measurement_unit']
                )
                if created:
                    added_count += 1
                    # Увеличиваем счётчик добавленных ингредиентов
                else:
                    existing_count += 1
                    # Увеличиваем счётчик существующих ингредиентов

        # Выводим результаты
        self.stdout.write(
            self.style.SUCCESS(f'Добавлено ингредиентов: {added_count}'))
        self.stdout.write(
            self.style.WARNING(f'Существующих ингредиентов: {existing_count}'))
