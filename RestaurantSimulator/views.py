import re
from urllib.parse import urlencode

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from . import models
from .queries import (
    get_total_tokens_used,
    get_model_name,
    get_model_temperature,
    get_diet_distribution,
    get_all_favorite_foods,
)
import json


@login_required
def index(request):
    """Index page view for ElephantChat"""

    # On first load set the filters to vegetarian/vegan
    if request.GET.get("first_load_flag", 'false') != "true":
        query_params = request.GET.copy()
        query_params['preference'] = ["vegetarian", "vegan"]
        query_params['first_load_flag'] = 'true'
        query_string = urlencode(query_params, doseq=True)
        return redirect(f"{request.path}?{query_string}")


    chats_qs = models.SimulatedChatThread.objects.all().order_by("-id")
    # If the user selected one or more preferences, filter the queryset by the JSON field
    if selected_prefs := request.GET.getlist("preference"):
        chats_qs = chats_qs.filter(
            extracted_answers__diet__in=[p.capitalize() for p in selected_prefs],
        )

    details_view = None
    if chat_id := request.GET.get("chat_id"):
        if chat_thread := models.SimulatedChatThread.objects.filter(id=chat_id).first():


            # Unnecessary check now that all fields are populated
            if top3_dishes := chat_thread.extracted_answers.get("top3_dishes"):
                messages = chat_thread.messages.all().order_by("timestamp")

                dish_pattern = re.compile(
                    r"\b(" + "|".join(map(re.escape, top3_dishes)) + r")\b"
                )

                for message in messages:
                    message.content = dish_pattern.sub(
                        lambda match: (f"<b class='dish-marker' data-dish='{match.group(0)}'>{match.group(0)}</b>"),
                        message.content,
                    )

                details_view = {
                    "details": chat_thread,
                    "messages": messages,
                    "waiter_tokens_used": get_total_tokens_used(
                        chat_thread, models.RoleType.WaiterBot
                    ),
                    "waiter_model": get_model_name(
                        chat_thread, models.RoleType.WaiterBot
                    ),
                    "waiter_temperature": get_model_temperature(
                        chat_thread, models.RoleType.WaiterBot
                    ),
                    "customer_model": get_model_name(
                        chat_thread, models.RoleType.CustomerBot
                    ),
                    "customer_temperature": get_model_temperature(
                        chat_thread, models.RoleType.CustomerBot
                    ),
                    "customer_tokens_used": get_total_tokens_used(
                        chat_thread, models.RoleType.CustomerBot
                    ),
                }

    # Prepare stats and a JSON representation of dish counts for the client-side word cloud
    # Only include foods that are mentioned at least twice to make the cloud easier to read
    dishes_dist = get_all_favorite_foods(chats_qs)
    dishes_dist = {
        k: v for k, v in dishes_dist.items() if v > 1
    }


    return render(
        request,
        "index.html",
        {
            "chats": chats_qs,
            "chat_stats": {
                "diet_dist": get_diet_distribution(),
                "count": models.SimulatedChatThread.objects.all().count(),
            },
            "dishes_json": json.dumps(dishes_dist),
            "detail_view": details_view,
            "selected_preferences": selected_prefs,
        },
    )
