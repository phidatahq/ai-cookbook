from typing import Optional

from phi.llm.openai import OpenAIChat
from phi.conversation import Conversation
from phi.tools.website import WebsiteTools

from llm.settings import llm_settings
from llm.storage import website_conversation_storage
from llm.knowledge_base import website_knowledge_base


def get_website_auto_conversation(
    user_name: Optional[str] = None,
    conversation_id: Optional[str] = None,
    debug_mode: bool = False,
) -> Conversation:
    """Get an autonomous conversation with the Website knowledge base"""

    return Conversation(
        id=conversation_id,
        user_name=user_name,
        llm=OpenAIChat(
            model=llm_settings.gpt_4,
            max_tokens=llm_settings.default_max_tokens,
            temperature=llm_settings.default_temperature,
        ),
        storage=website_conversation_storage,
        knowledge_base=website_knowledge_base,
        debug_mode=debug_mode,
        monitoring=True,
        function_calls=True,
        show_function_calls=True,
        tools=[WebsiteTools(knowledge_base=website_knowledge_base)],
        system_prompt="""\
        You are an assistant named 'phi' designed to answer questions about website contents.
        You have access to functions to search a knowledge base of website contents.
        You also have access to functions to add new websites to the knowledge base.
        Only add 'https://' websites.

        Follow these guidelines:
        - Always search the knowledge base.
        - Add websites to the knowledge base when needed. Only add 'https://' websites.
        - If you don't know the answer, say 'I don't know'.
        - Do not use phrases like 'based on the information provided'.
        - Use markdown to format your answers.
        - Keep your answers short and concise, under 5 sentences.
        """,
        user_prompt_function=lambda message, **kwargs: f"""\
        Respond to the following message:
        USER: {message}
        ASSISTANT:
        """,
        meta_data={"conversation_type": "AUTO"},
    )
