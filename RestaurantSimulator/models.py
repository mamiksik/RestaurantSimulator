from django.db import models

class ChatMessage(models.Model):
    class RoleType(models.TextChoices):
        System = 'System'
        User = 'User'
        Assistant = 'Assistant'

    thread = models.ForeignKey("SimulatedChatThread", on_delete=models.CASCADE, related_name="messages")

    role = models.CharField(max_length=255, choices=RoleType.choices)
    """The role of the message sender, which can be "system", "user, or "assistant"""

    content = models.TextField()
    """The content of the chat message."""

    timestamp = models.DateTimeField()
    """The timestamp when the chat message was generated"""

    def __str__(self):
        return f"{self.role}: {self.content[:50]}..."


class SimulatedChatThread(models.Model):
    """A simulated chat thread between a customer and a waiter."""

    id = models.AutoField(primary_key=True)
