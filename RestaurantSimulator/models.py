from django.db import models

class RoleType(models.TextChoices):
    CustomerBot = 'CustomerBot'
    WaiterBot = 'WaiterBot'

class ChatMessage(models.Model):
    thread = models.ForeignKey("SimulatedChatThread", on_delete=models.CASCADE, related_name="messages")

    role = models.CharField(max_length=255, choices=RoleType.choices)
    """The role of the message sender, either 'CustomerBot' or 'WaiterBot'."""

    content = models.TextField()
    """The content of the chat message."""

    timestamp = models.DateTimeField()
    """The timestamp when the chat message was generated"""

    completion_tokens = models.IntegerField(default=-1)
    """ Tokens produced generating message (-1 is sentinel value) """

    prompt_tokens = models.IntegerField(default=-1)
    """ Prompt size in tokens (-1 is sentinel value) """

    total_tokens = models.IntegerField(default=-1)
    """ Total number of tokens read and produced for this message (-1 is sentinel value) """

    model = models.CharField(max_length=255, null=True, blank=True)
    """ Model used to generate this message """

    temperature = models.FloatField(null=True, blank=True)
    """ Model temperature used to generate this message """

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
    """ The extracted answers from the chat conversation
        SQLLite does not handle lists well, to model this as a table we would need M2M relationship,
        that is overly complex for this use-case. For now JSON field is sufficient as SQLLite also
        support queries on json fields
    """