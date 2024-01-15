from phi.assistant import Assistant
from phi.llm.openai import OpenAIChat

from llm.settings import llm_settings

assistant = Assistant(
    llm=OpenAIChat(
        model=llm_settings.gpt_4_vision,
        max_tokens=llm_settings.default_max_tokens,
        temperature=llm_settings.default_temperature,
    ),
    monitoring=True,
)

# Single Image
assistant.print_response(
    [
        {"type": "text", "text": "What's in this image, describe in 1 sentence"},
        {
            "type": "image_url",
            "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg",
        },
    ]
)

# Multiple Images
assistant.print_response(
    [
        {
            "type": "text",
            "text": "Is there any difference between these. Describe them in 1 sentence.",
        },
        {
            "type": "image_url",
            "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg",
        },
        {
            "type": "image_url",
            "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg",
        },
    ]
)
