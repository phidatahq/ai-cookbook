from phi.task.llm import LLMTask
from phi.conversation import Conversation
from pydantic import BaseModel, Field


class StoryTheme(BaseModel):
    setting: str = Field(
        ...,
        description="This is the context of the story. If not available, provide a random setting.",
    )
    genre: str = Field(..., description="This is the genre of the story. If not provided, select horror.")


get_story_theme = LLMTask(
    system_prompt="Generate a theme for a story.",
    output_model=StoryTheme,
    show_output=False,
)

write_story = LLMTask(system_prompt="Write a 2 sentence story about the users message.")

give_story_a_name = LLMTask(
    system_prompt="Give the users story a name. Start with `Name:`. Don't surround with quotes."
)

story_conversation = Conversation(
    tasks=[get_story_theme, write_story, give_story_a_name], monitoring=True, debug_mode=True
)
story_conversation.print_response("new york")
