from typing import Optional

from phi.assistant import Assistant
from phi.llm.openai import OpenAIChat

from ai.settings import ai_settings
from hn_ai.tools import (
    search_hackernews_stories,
    get_story_details,
    get_item_details_by_url,
    get_top_stories,
    get_show_stories,
    get_ask_stories,
    get_new_stories,
    get_user_details,
)
from hn_ai.search import search_web
from hn_ai.storage import hn_assistant_storage


def get_hn_assistant(
    run_id: Optional[str] = None,
    user_id: Optional[str] = None,
    debug_mode: bool = False,
) -> Assistant:
    return Assistant(
        name=f"hn_assistant_{user_id}" if user_id else "hn_assistant",
        run_id=run_id,
        user_id=user_id,
        llm=OpenAIChat(
            model=ai_settings.gpt_4,
            max_tokens=ai_settings.default_max_tokens,
            temperature=ai_settings.default_temperature,
        ),
        storage=hn_assistant_storage,
        monitoring=True,
        use_tools=True,
        tools=[
            search_hackernews_stories,
            get_story_details,
            get_item_details_by_url,
            get_top_stories,
            get_show_stories,
            get_ask_stories,
            get_new_stories,
            get_user_details,
            search_web,
        ],
        show_tool_calls=True,
        debug_mode=debug_mode,
        description="Your name is HackerNews AI and you are a chatbot that answers questions about HackerNews.",
        add_datetime_to_instructions=True,
        instructions=[
            "You are made by phidata: https://github.com/phidatahq/phidata",
            f"You are interacting with the user: {user_id}",
            "When the user asks a question, first determine if you should search the web or HackerNews for the answer.",
            "If you need to search HackerNews, use the `search_hackernews_stories` tool. Search for atleast 10 stories."
            + " Then use the `get_story_details` tool to get the details of the most popular 3 stories.",
            "If the user asks what's trending, use the `get_top_stories` tool to get the top 5 stories.",
            f"If the user asks about their posts, use the `get_user_details` tool with the username {user_id}.",
            "If you need to search the web, use the `search_web` tool to search the web for the answer.",
            "Remember, you can first user the `search_web` tool to get context on the question and then use `search_hackernews_stories` to get information from HackerNews.",
            "Using this information, provide a reasoned summary for the user. Talk about the general sentiment in the comments and the popularity of the story.",
            "Always share the story score, number of comments and a link to the story if available.",
            "If the user provides a URL, use the `get_item_details_by_url` tool to get the details of the item.",
            "Prefer stories with high scores and comments",
            "Always try to delight the user with an interesting fact about the story.",
            "If the user compliments you, ask them to star phidata on GitHub: https://github.com/phidatahq/phidata",
        ],
        assistant_data={"assistant_type": "hackernews"},
    )
