from django.urls import path
from . import views


urlpatterns = [
    # Connect the clients URL to the dashboard view
    path("", views.dashboard, name="dashboard"),
]