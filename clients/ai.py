
from django.conf import settings
from google import genai
from google.genai import types


# Read the Gemini API key from Django settings.
api_key = settings.GEMINI_API_KEY

# Create the Gemini client only when an API key is available.
gemini_client = (
    genai.Client(api_key=api_key)
    if api_key
    else None
)


def ask_gemini(client_context, conversation_history):
    """
    Send business context and previous messages to Gemini.
    Return the generated response as text.
    """

    # Stop if the API key is missing.
    if gemini_client is None:
        raise ValueError("The Gemini API key is missing.")

    # Tell Gemini its role and explain how to handle research questions.
      # Tell Gemini its role and explain how to handle research questions.
    system_instruction = (
        "You are a Business Research AI Assistant. "
        "Help the operator research businesses, markets, competitors, "
        "customers, industry trends and business opportunities. "
        "Use the supplied client information as context. "
        "Distinguish verified facts from estimates and uncertainty. "
        "Never invent sources, statistics or research findings. "
        "Explain when current information requires external verification. "
        "Provide practical, clear and well-organized answers.\n\n"
                "FORMATTING RULES:\n"
        "- Write in plain text only. Never use special characters for formatting.\n"
        "- Do not use #, *, **, _, `, ~, | or --- anywhere.\n"
        "- Do not use tables.\n"
        "- Write each section title on its own line, in plain words.\n"
        "- For lists, start each item on a new line with a hyphen and a space.\n"
        "- For steps, number them like 1. 2. 3.\n"
        "- Keep paragraphs short and separate them with a blank line.\n"
        "- For simple questions, answer briefly without section titles.\n\n"
        "- For simple questions, answer briefly without headings.\n"
        "- End with a short next-step suggestion when relevant.\n\n"
        f"CLIENT INFORMATION:\n{client_context}"
    )

    # Prepare the conversation in the format Gemini expects.
    contents = []

    # Process each saved message in chronological order.
    for message in conversation_history:

        # Convert the sender into a Gemini role.
        if message.sender == "user":
            role = "user"
        else:
            role = "model"

        # Add the message content to the conversation.
        contents.append(
            types.Content(
                role=role,
                parts=[
                    types.Part.from_text(
                        text=message.content
                    )
                ]
            )
        )

    # Ask Gemini to generate an answer.
    response = gemini_client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=contents,
        # Pass the system instruction (the AI's role and rules) to Gemini as part of the request settings
        config=types.GenerateContentConfig(
            system_instruction=system_instruction
        )
    )

    # Return the answer to the Django view.
    return response.text
