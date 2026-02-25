from django import template

register = template.Library()


@register.filter(name="dietary_preference_to_icon")
def dietary_preference_to_icon(value):
    normalized_value = value.strip().lower()
    return {
        "vegetarian": "🥦",
        "vegan": "🌱",
        "pescatarian": "🐟",
        "omnivore": "🍽️",
    }.get(normalized_value, "❓")

@register.filter(name="dietary_preference_to_color")
def dietary_preference_to_color(value):
    normalized_value = value.strip().lower()
    return {
        "vegetarian": "bg-green-500 text-green-100 text-xs",
        "vegan": "bg-green-700",
        "pescatarian": "bg-blue-500",
        "omnivore": "bg-red-500",
    }.get(normalized_value, "gray-500")

