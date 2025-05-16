from rest_framework import serializers

from food.constants import MAX_AMOUNT, MIN_AMOUNT


def validate_tags(tags):
    if not tags:
        raise serializers.ValidationError("Выберите теги")

    unique_tags = set()
    for tag in tags:
        if tag in unique_tags:
            raise serializers.ValidationError(f"Тэг '{tag}' дублируется.")
        unique_tags.add(tag)


def validate_ingredients(ingredients):
    if not ingredients:
        raise serializers.ValidationError("Выберите хотя бы один ингредиент")

    ingredient_ids = set()
    for ingredient in ingredients:
        ingredient_id = ingredient["ingredient"].id

        if ingredient_id in ingredient_ids:
            raise serializers.ValidationError(
                "Ингредиенты не должны дублироваться.")
        ingredient_ids.add(ingredient_id)

        amount = ingredient['amount']

        if isinstance(amount, str):
            amount = int(amount)

        if amount < 1:
            raise serializers.ValidationError(
                "Количество должно быть целым числом и больше нуля.")


def validate_image(image):
    if not image:
        raise serializers.ValidationError("Добавьте изображение блюда.")


def validate_cooking_time(cooking_time):
    if cooking_time < MIN_AMOUNT or cooking_time > MAX_AMOUNT:
        raise serializers.ValidationError(
            "Укажите время готовки от 1 до 32000 минут.")


def validate_recipe(attrs):
    validate_tags(attrs.get("tags"))
    validate_ingredients(attrs.get("ingredients"))
    validate_image(attrs.get("image"))
    validate_cooking_time(attrs.get("cooking_time"))
    return attrs


def validate_amount(self, value):
    """Проверка валидности значения amount."""
    if value < MIN_AMOUNT or value > MAX_AMOUNT:
        raise serializers.ValidationError(
            f"Колл-во должно быть от {MIN_AMOUNT} до {MAX_AMOUNT}."
        )
    return value
