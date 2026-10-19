from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages

from .models import Client, Conversation, Message
from .ai import ask_gemini


# Show the dashboard page listing all clients as cards.
def dashboard(request):
    # Retrieve all clients from the database.
    clients = Client.objects.all()

    # Display the dashboard and its client cards.
    return render(request, "clients/dashboard.html", {"clients": clients})


# Entry point when a client card is opened: redirects to that client's latest
# conversation, creating a first one if none exists.
def client_workspace(request, client_id):
    # Find the selected client or return a 404 page.
    client = get_object_or_404(Client, id=client_id)

    # Find the most recently updated conversation for this client.
    conversation = client.conversations.order_by("-updated_at", "-id").first()

    # Create a first conversation if the client has no chat history.
    if conversation is None:
        conversation = Conversation.objects.create(client=client, title="New chat")

    # Redirect to the selected conversation.
    return redirect(
        "conversation_workspace", client_id=client.id, conversation_id=conversation.id
    )


# Handle the "New chat" button: creates a fresh empty conversation for the
# client and opens it, keeping all existing chats.
def new_conversation(request, client_id):
    # Find the client that needs a new conversation.
    client = get_object_or_404(Client, id=client_id)

    # Create a new conversation without deleting existing chats.
    conversation = Conversation.objects.create(client=client, title="New chat")

    # Open the newly created conversation.
    return redirect(
        "conversation_workspace", client_id=client.id, conversation_id=conversation.id
    )


# Main chat page. On GET it displays the conversation and sidebar; on POST it
# saves the user's question, gets an answer from Gemini, saves it, and redirects
# back to the same page.
def conversation_workspace(request, client_id, conversation_id):
    # Retrieve the client.
    client = get_object_or_404(Client, id=client_id)

    # Retrieve a conversation that belongs to this client.
    conversation = get_object_or_404(Conversation, id=conversation_id, client=client)

    # Process the submitted question when the form is posted.
    if request.method == "POST":

        # Read the message from the submitted form.
        question = request.POST.get("message", "").strip()

        # Reject empty messages.
        if not question:
            messages.error(request, "Please enter a research question.")

            return redirect(
                "conversation_workspace",
                client_id=client.id,
                conversation_id=conversation.id,
            )

        # Check whether this is the first message in the conversation.
        is_first_message = not conversation.messages.exists()

        # Save the user's question before calling Gemini.
        Message.objects.create(
            conversation=conversation, sender="user", content=question
        )

        # Use the first question as the conversation title.
        # checks whether the question is longer than 50 characters.
        # if it is keeps the first 47 characters and adds .... That makes exactly 50 characters, which keeps the sidebar tidy.
        if is_first_message:
            conversation.title = (
                question[:47] + "..." if len(question) > 50 else question
            )

            # Update the conversation's last modified timestamp.
        conversation.save()

        # Prepare the client's business information for Gemini.
        client_context = (
            f"Business name: {client.business_name}\n"
            f"Industry: {client.industry}\n"
            f"Description: {client.description}"
        )

        # Retrieve messages in chronological order.
        conversation_history = list(conversation.messages.order_by("created_at", "id"))

        # Generate an answer using the client's details and history.
        answer = ask_gemini(client_context, conversation_history)

        # Save the AI answer in the same conversation.
        Message.objects.create(conversation=conversation, sender="ai", content=answer)

        # Update the conversation's timestamp.
        conversation.save()

        # Redirect after POST to avoid accidental resubmission on refresh.
        return redirect(
            "conversation_workspace",
            client_id=client.id,
            conversation_id=conversation.id,
        )

    # Retrieve saved messages for the selected conversation.
    conversation_history = conversation.messages.all()

    # Retrieve this client's conversations for the sidebar.
    conversations = client.conversations.order_by("-updated_at", "-id")

    # Render the workspace with all required context.
    return render(
        request,
        "clients/workspace.html",
        {
            "client": client,
            "conversation": conversation,
            "conversation_history": conversation_history,
            "conversations": conversations,
        },
    )
