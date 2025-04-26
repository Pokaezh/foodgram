from rest_framework import serializers

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
        ingredient_id = ingredient.get("ingredient").id
        if ingredient_id in ingredient_ids:
            raise serializers.ValidationError("Ингредиенты не должны дублироваться.")
        ingredient_ids.add(ingredient_id)

        amount = ingredient.get('amount')
        
        # Преобразуем amount в целое число, если это строка
        if isinstance(amount, str):
            try:
                amount = int(amount)
            except ValueError:
                raise serializers.ValidationError("Количество должно быть целым числом.")

        if amount is None or amount < 1:
            raise serializers.ValidationError("Должен быть указан хотя бы один ингредиент с количеством больше 0.")


def validate_image(image):
    if not image:
        raise serializers.ValidationError("Добавьте изображение блюда.")

def validate_cooking_time(cooking_time):
    if cooking_time is None or cooking_time < 1:
        raise serializers.ValidationError("Укажите время готовки.")


def validate_recipe(attrs):
    validate_tags(attrs.get("tags"))
    validate_ingredients(attrs.get("ingredients"))
    validate_image(attrs.get("image"))
    validate_cooking_time(attrs.get("cooking_time"))
    return attrs