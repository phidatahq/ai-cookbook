from typing import Optional
from arxiv import Result as ArxivPaper
from phi.assistant import Assistant, AssistantRun
from phi.llm.openai import OpenAIChat

from ai.settings import ai_settings
from arxiv_ai.tools import ArxivTools
from arxiv_ai.storage import latent_space_arxiv_bot_storage
from utils.log import logger


def get_discussion_assistant(
    user_id: str,
    thread_id: str,
    paper: Optional[ArxivPaper] = None,
    debug_mode: bool = True,
) -> Optional[Assistant]:
    arxiv_tools = ArxivTools(user_id="latent_space")
    paper_data = None
    paper_title = None
    paper_id = None

    # ------------ FIX FROM HERE ------------
    # TODO: this code has bugs
    if paper is None:
        assistant_run: Optional[AssistantRun] = latent_space_arxiv_bot_storage.read(run_id=thread_id)
        if assistant_run is not None:
            paper_data = assistant_run.run_data.get("paper", None)
            logger.info(f"Paper found in run data: {paper_data}")
    else:
        paper_title = paper.title
        paper_id = paper.get_short_id()

    if paper_title is None:
        if paper_data is None:
            return None
        paper_title = paper_data.get("title")
        paper_id = paper_data.get("id")
    # ------------ FIX TILL HERE ------------

    instructions = [
        "You are made by phidata: https://github.com/phidatahq/phidata",
        f"You are interacting with the user: `{user_id}`",
        f"Your goal is to help the use answer questions about the ArXiv paper: {paper_title} (id: {paper_id})",
        "The audience has knowledge of the field, so focus on the main contributions and findings of the paper",
        "Mention statistics and significant wins of the paper",
    ]

    return Assistant(
        name="latent_space_arxiv_discussion",
        run_id=thread_id,
        user_id=user_id,
        llm=OpenAIChat(
            model=ai_settings.gpt_4,
            max_tokens=ai_settings.default_max_tokens,
            temperature=ai_settings.default_temperature,
        ),
        storage=latent_space_arxiv_bot_storage,
        description="Your name is Arxiv AI and you are a designed to help users understand technical ArXiv papers.",
        monitoring=True,
        use_tools=True,
        debug_mode=debug_mode,
        instructions=instructions,
        tools=[arxiv_tools],
        add_chat_history_to_messages=True,
        num_history_messages=4,
        run_data={"paper": {"title": paper_title, "id": paper_id}},
    )
