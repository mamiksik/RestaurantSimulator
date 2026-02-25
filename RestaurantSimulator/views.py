from django.shortcuts import render
from . import models

def index(request):
    """ Index page view for ElephantChat """

    chats_qs = models.SimulatedChatThread.objects.all().order_by('-id')
    # If the user selected one or more preferences, filter the queryset by the JSON field
    if selected_prefs := request.GET.getlist('preference'):
        chats_qs = chats_qs.filter(
            extracted_answers__dietary_preference__in=[p.capitalize() for p in selected_prefs],
        )

    details_view = None
    if chat_id := request.GET.get('chat_id'):
        if chat_thread := models.SimulatedChatThread.objects.filter(id=chat_id).first():
            top3_dishes = chat_thread.extracted_answers['top_3_favorite_foods']
            messages = chat_thread.messages.all().order_by('timestamp')
            for msg in messages:
                for idx, dish in enumerate(top3_dishes):
                    if dish in msg.content:
                        msg.content = msg.content.replace(dish, f"<span class='dish-marker' data-dish='{dish}'>{dish}</span>")

            details_view = {
                'details': chat_thread,
                'messages': messages
            }

    return render(request, 'chat_index.html', {
        'chats': chats_qs,
        'detail_view': details_view,
        'selected_preferences': selected_prefs,
    })