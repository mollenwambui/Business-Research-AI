#he render() function is a shortcut that combines an HTTP request and a context dictionary with an HTML template to return a fully rendered HttpResponse object.
from django.shortcuts import get_object_or_404, render
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

def client_workspace(request, client_id):
    # Find the requested client or show a 404 page if it does not exist
    client = get_object_or_404(Client, id=client_id)

    # Send the selected client to the workspace template
    return render(
        request,
        "clients/workspace.html",
        {
            "client": client
        }
    )