from django.contrib import admin
from .models import ChatMessage, SimulatedChatThread

# Register your models here.
admin.site.register(ChatMessage)
admin.site.register(SimulatedChatThread)
