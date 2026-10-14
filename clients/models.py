
from django.db import models


class Client(models.Model):
    # Store the client's contact person's name
    name = models.CharField(max_length=200)

    # Store the client's business name
    business_name = models.CharField(max_length=200)

    # Store the client's industry
    industry = models.CharField(max_length=100, blank=True)

    # Store a description of the client's business
    description = models.TextField(blank=True)

    # Record when the client was created
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # Display the business name in Django Admin
        return self.business_name


class Conversation(models.Model):
    # Link each conversation to the client it belongs to
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name="conversations"
    )

    # Give the conversation a descriptive title
    title = models.CharField(max_length=200, default="Business Research")

    # Record when the conversation was created
    created_at = models.DateTimeField(auto_now_add=True)

    # Record when the conversation was last updated
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        # Display the title and business name
        return f"{self.title} - {self.client.business_name}"


class Message(models.Model):
    # Define the available message sender types
    SENDER_CHOICES = [
        ("user", "User"),
        ("ai", "AI Assistant"),
    ]

    # Link each message to its conversation
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="messages"
    )

    # Store whether the message came from the user or AI
    sender = models.CharField(
        max_length=10,
        choices=SENDER_CHOICES
    )

    # Store the actual message text
    content = models.TextField()

    # Record when the message was created
    created_at = models.DateTimeField(auto_now_add=True)
     
     #class Meta is an inner class where you put model-level options, i.e. settings about the model itself rather than its fields.
    class Meta:
        # Display messages in the order they were created
        ordering = ["created_at", "id"]

    def __str__(self):
        # Display the sender and a short preview of the message
        return f"{self.sender}: {self.content[:50]}"
