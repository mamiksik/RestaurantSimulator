from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from . import models
from .queries import (
    get_total_tokens_used,
    get_model_name,
    get_model_temperature,
    get_diet_distribution,
    get_all_favorite_foods,
)


@login_required
def index(request):
    """Index page view for ElephantChat"""

    chats_qs = models.SimulatedChatThread.objects.all().order_by("-id")
    # If the user selected one or more preferences, filter the queryset by the JSON field
    if selected_prefs := request.GET.getlist("preference"):
        print(selected_prefs)
        chats_qs = chats_qs.filter(
            extracted_answers__diet__in=[p.capitalize() for p in selected_prefs],
        )

    details_view = None
    if chat_id := request.GET.get("chat_id"):
        if chat_thread := models.SimulatedChatThread.objects.filter(id=chat_id).first():
            waiter_tokens_used = get_total_tokens_used(
                chat_thread, models.RoleType.WaiterBot
            )
            customer_tokens_used = get_total_tokens_used(
                chat_thread, models.RoleType.CustomerBot
            )

            if top3_dishes := chat_thread.extracted_answers.get("top3_dishes"):
                messages = chat_thread.messages.all().order_by("timestamp")
                for msg in messages:
                    for idx, dish in enumerate(top3_dishes):
                        if dish in msg.content:
                            msg.content = msg.content.replace(
                                dish,
                                f"<span class='dish-marker' data-dish='{dish}'>{dish}</span>",
                            )

                details_view = {
                    "details": chat_thread,
                    "messages": messages,
                    "waiter_tokens_used": waiter_tokens_used,
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
                    "customer_tokens_used": customer_tokens_used,
                }

    return render(
        request,
        "chat_index.html",
        {
            "chats": chats_qs,
            "chat_stats": {
                "diet_dist": get_diet_distribution(),
                "dishes_dist": get_all_favorite_foods(),
                "count": models.SimulatedChatThread.objects.all().count(),
            },
            "detail_view": details_view,
            "selected_preferences": selected_prefs,
        },
    )
