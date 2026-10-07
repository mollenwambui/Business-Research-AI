from django.urls import path
from . import views


urlpatterns = [
    # Connect the clients URL to the dashboard view
    path("", views.dashboard, name="dashboard"),

    # Connect a specific client ID to that client's workspace
    path("<int:client_id>/", views.client_workspace, name="client_workspace"),
]