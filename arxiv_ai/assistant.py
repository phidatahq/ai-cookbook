import json
from typing import Optional, List

from phi.assistant import Assistant
from phi.llm.openai import OpenAIChat

from ai.settings import ai_settings
from hn_ai.search import search_web
from arxiv_ai.storage import arxiv_assistant_storage
from arxiv_ai.tools import ArxivTools
from arxiv_ai.knowledge import get_arxiv_knowledge_base_for_user
from utils.log import logger


def get_arxiv_assistant(
    user_id: str,
    run_id: Optional[str] = None,
    debug_mode: bool = False,
) -> Assistant:
    arxiv_tools = ArxivTools(user_id=user_id)

    introduction = "Hi, I am Arxiv AI, built by [phidata](https://github.com/phidatahq/phidata)."

    instructions = [
        "You are made by phidata: https://github.com/phidatahq/phidata",
        f"You are interacting with the user: {user_id}",
        "Your goal is to answer questions from a knowledge base of ArXiv papers.",
        "When the user asks a question, first use the `get_document_summaries` to find atleast 5 relevant ArXiv papers in the knowledge base.",
        "If you cannot find a relevant paper in the knowledge base, use the `search_arxiv_and_add_to_knowledge_base` tool to search ArXiv for relevant papers and add them to the knowledge base.",
        "If the user provides a link then use `add_arxiv_papers_to_knowledge_base` tool to add the paper to the knowledge base.",
        "If the user is asking to summarize a specific paper, use the results of the `get_document_summaries` tool and provide a simple explanation for the paper.",
        "If the user is asking a question from a specific paper, use the `search_document` tool to get context from the specific paper.",
        "If the user is asking about the content of the knowledge base use `get_document_names` tool to get the list of documents.",
    ]

    instructions.extend(
        [
            "You can also search the entire knowledge base using the `search_knowledge_base` tool.",
            "Keep your conversation light hearted and fun.",
            "Using information from the document, provide the user with a concise and relevant answer.",
            "If you cannot find the information in the knowledge base, think if you can find it on the web. If you can find the information on the web, use the `search_web` tool",
            "When searching the knowledge base, search for at least 3 documents.",
            "When getting document contents, get at least 5000 words so you get the first few pages.",
            "If the user compliments you, ask them to star phidata on GitHub: https://github.com/phidatahq/phidata",
        ]
    )

    return Assistant(
        name=f"arxiv_assistant_{user_id}" if user_id else "arxiv_assistant",
        run_id=run_id,
        user_id=user_id,
        llm=OpenAIChat(
            model=ai_settings.gpt_4,
            max_tokens=ai_settings.default_max_tokens,
            temperature=ai_settings.default_temperature,
        ),
        storage=arxiv_assistant_storage,
        monitoring=True,
        use_tools=True,
        introduction=introduction,
        tools=[search_web, arxiv_tools],
        knowledge_base=get_arxiv_knowledge_base_for_user(user_id),
        show_tool_calls=True,
        debug_mode=debug_mode,
        description="Your name is Arxiv AI and you are a designed to help users understand technical ArXiv papers.",
        add_datetime_to_instructions=True,
        instructions=instructions,
    )
