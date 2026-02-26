from django import template

register = template.Library()


@register.filter(name="diet")
def diet_to_icon(value):
    normalized_value = value.strip().lower()
    return {
        "vegetarian": "🥦",
        "vegan": "🌱",
        "pescatarian": "🐟",
        "omnivore": "🍽️",
    }.get(normalized_value, "❓")
