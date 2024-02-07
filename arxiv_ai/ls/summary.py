import json
from textwrap import dedent

from arxiv import Result as ArxivPaper
from phi.assistant import Assistant
from phi.llm.openai import OpenAIChat

from ai.settings import ai_settings
from arxiv_ai.tools import ArxivTools
from arxiv_ai.storage import latent_space_arxiv_bot_storage


def get_summary_assistant(
    user_id: str,
    thread_id: str,
    paper: ArxivPaper,
    debug_mode: bool = True,
) -> Assistant:
    paper_details = {
        "title": paper.title,
        "entry_id": paper.entry_id,
        "updated": paper.updated.isoformat() if paper.updated else None,
        "authors": [author.name for author in paper.authors],
        "primary_category": paper.primary_category,
        "categories": paper.categories,
        "published": paper.published.isoformat() if paper.published else None,
        "pdf_url": paper.pdf_url,
        "links": [link.href for link in paper.links],
        "summary": paper.summary,
        "comment": paper.comment,
    }

    arxiv_tools = ArxivTools(user_id="latent_space")
    try:
        paper_content = arxiv_tools.get_document_contents(paper.get_short_id(), limit=7000)
    except Exception as e:
        paper_content = ""

    try:
        if paper_content == "":
            arxiv_tools.add_arxiv_papers_to_knowledge_base([paper.get_short_id()])
            paper_content = arxiv_tools.get_document_contents(paper.get_short_id(), limit=7000)
    except Exception as e:
        paper_content = ""

    instructions = [
        "You are made by phidata: https://github.com/phidatahq/phidata",
        f"You are interacting with the user: `{user_id}`",
        "Your goal is to provide a summary of the following ArXiv paper in 3 bullet points or less",
        "The audience has knowledge of the field, so focus on the main contributions and findings of the paper",
        "Mention statistics and significant wins of the paper",
        "You will also be provided with the first 7000 words of the paper to help you provide a relevant answer",
    ]

    return Assistant(
        name="latent_space_arxiv_summary",
        run_id=thread_id,
        user_id=user_id,
        llm=OpenAIChat(
            model=ai_settings.gpt_4,
            max_tokens=ai_settings.default_max_tokens,
            temperature=ai_settings.default_temperature,
        ),
        storage=latent_space_arxiv_bot_storage,
        monitoring=True,
        use_tools=True,
        debug_mode=debug_mode,
        instructions=instructions,
        add_to_system_prompt=dedent(
            """\
        <arxiv_paper>
        {}
        </arxiv_paper>

        <paper_content>
        {}
        </paper_content>
        """.format(json.dumps(paper_details, indent=4), paper_content)
        ),
        run_data={"paper": {"title": paper.title, "id": paper.get_short_id()}},
    )
