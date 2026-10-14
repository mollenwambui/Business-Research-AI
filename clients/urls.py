from django.urls import path
from . import views


urlpatterns = [
    # Display all clients.
    path("", views.dashboard, name="dashboard"),

    # Open a client's latest conversation.
    path("<int:client_id>/", views.client_workspace, name="client_workspace"),

    # Create a new conversation for a client.
    path("<int:client_id>/new/", views.new_conversation, name="new_conversation"),

    # Open a specific conversation belonging to a client.
    path("<int:client_id>/chat/<int:conversation_id>/", views.conversation_workspace, name="conversation_workspace"),
]