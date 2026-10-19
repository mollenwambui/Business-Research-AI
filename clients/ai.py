
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
    Send business context and conversation history to Gemini.
    Allow Gemini to use research and analysis tools.
    Return the generated response with available source links.
    """

    # Stop if the API key is missing.
    if gemini_client is None:
        raise ValueError("The Gemini API key is missing.")

    # Define the AI assistant's role and behaviour.
    system_instruction = (
        "You are a Business Research AI Assistant. "
        "Help the operator research businesses, markets, competitors, "
        "customers, industry trends and business opportunities. "

        "Use the supplied client information as context. "

        "Use Google Search for current information and fact checking. "
        "Use URL Context to analyse webpages supplied by the operator. "
        "Use code execution for calculations, projections and data analysis. "
        "Use Google Maps when researching real businesses and locations. "

        "Use tools when they are relevant to the question. "
        "Distinguish verified facts from estimates and uncertainty. "
        "Never invent sources, statistics or research findings. "
        "If the available evidence is incomplete, explain the limitation. "
        "Cite relevant sources when available. "
        "Provide practical, clear and well-organized answers.\n\n"

        "FORMATTING RULES:\n"
        "Use plain text with clear section headings.\n"
        "Do not use Markdown tables.\n"
        "Use numbered lists for procedures and simple lists for items.\n"
        "Keep paragraphs short and readable.\n"
        "For simple questions, answer briefly without headings.\n"
        "End with a practical next step when relevant.\n\n"

        f"CLIENT INFORMATION:\n{client_context}"
    )

    # Prepare the conversation in the format Gemini expects.
    contents = []

    # Process saved messages in chronological order.
    for message in conversation_history:

        # Map Django message senders to Gemini roles.
        if message.sender == "user":
            role = "user"
        else:
            role = "model"

        # Add each saved message to the conversation history.
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

    # Enable the four built-in Gemini tools.
    tools = [
        # Search the web for current information.
        types.Tool(
            google_search=types.GoogleSearch()
        ),

        # Read and analyse webpages supplied by the operator.
        types.Tool(
            url_context=types.UrlContext()
        ),

        # Execute code for calculations and data analysis.
        types.Tool(
            code_execution=types.ToolCodeExecution()
        ),

        # Research businesses and geographical locations.
        types.Tool(
            google_maps=types.GoogleMaps()
        ),
    ]

    # Send the conversation to Gemini with all four tools enabled.
    # Errors will propagate instead of silently retrying without tools.
    response = gemini_client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            tools=tools,
        ),
    )

    # Get the generated answer.
    answer = response.text or ""

    # Prepare collections for source links and duplicate detection.
    source_lines = []
    seen_urls = set()

    try:
        # Get the first response candidate from Gemini.
        candidate = response.candidates[0]

        # Grounding metadata contains source information when available.
        metadata = candidate.grounding_metadata

        if metadata and metadata.grounding_chunks:

            # Process each source returned in the grounding metadata.
            for chunk in metadata.grounding_chunks:

                # Get the web source, or the Maps source if no web source exists.
                source = (
                    getattr(chunk, "web", None)
                    or getattr(chunk, "maps", None)
                )

                # Skip chunks that contain neither source type.
                if source is None:
                    continue

                # URI means Uniform Resource Identifier.
                # It identifies a resource, such as a webpage.
                # A URL is a type of URI.
                # getattr returns None if the attribute does not exist.
                uri = getattr(source, "uri", None)

                # Get the source title if Gemini provides one.
                title = getattr(source, "title", None)

                # Skip sources that do not have a usable link.
                if not uri:
                    continue

                # Avoid adding the same source link more than once.
                if uri in seen_urls:
                    continue

                # Remember this URI to detect duplicates.
                seen_urls.add(uri)

                # Store the source title and link as plain text.
                # If no title exists, use the URI as the title.
                source_lines.append(
                    f"- {title or uri}: {uri}"
                )

    except (AttributeError, IndexError, TypeError):
        # Some responses may not contain grounding metadata.
        # Keep the AI answer even if source extraction is unavailable.
        pass

    # Append the collected source links below the AI's answer.
    # Put the heading on a new paragraph and each link on its own line.
    if source_lines:
        answer += "\n\nSources\n" + "\n".join(source_lines)

    # Return the answer to the Django view.
    return answer
