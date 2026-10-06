from django.shortcuts import render
from .models import Client


def dashboard(request):
    # Retrieve all existing clients from the database
    clients = Client.objects.all()

    # Send the clients to the dashboard template
    return render(
        request,
        "clients/dashboard.html",
        {
            "clients": clients
        }
    )