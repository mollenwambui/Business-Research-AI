
from django.contrib import admin
from .models import Client, Conversation, Message


# Register the Client model in Django Admin
admin.site.register(Client)

# Register the Conversation model in Django Admin
admin.site.register(Conversation)

# Register the Message model in Django Admin
admin.site.register(Message)
