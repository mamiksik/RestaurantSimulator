from typing import Literal

from django.db import models

class ChatMessage(models.Model):
    class RoleType(models.TextChoices):
        CustomerBot = 'CustomerBot'
        WaiterBot = 'WaiterBot'

    thread = models.ForeignKey("SimulatedChatThread", on_delete=models.CASCADE, related_name="messages")

    role = models.CharField(max_length=255, choices=RoleType.choices)
    """The role of the message sender, either 'CustomerBot' or 'WaiterBot'."""

    content = models.TextField()
    """The content of the chat message."""

    timestamp = models.DateTimeField()
    """The timestamp when the chat message was generated"""

    def __str__(self):
        return f"{self.role}: {self.content[:50]}..."


class SimulatedChatThread(models.Model):
    """A simulated chat thread between a customer and a waiter."""

    id = models.AutoField(primary_key=True)

    waiter_prompt = models.TextField()
    """The initial prompt given to the waiter to start the conversation."""

    customer_prompt = models.TextField()
    """The initial prompt given to the customer to start the conversation."""

    extracted_answers = models.JSONField(null=True, blank=True)
    """The extracted answers from the chat conversation, stored as a JSON object."""