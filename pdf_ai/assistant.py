import json
from typing import Optional, List

from phi.assistant import Assistant
from phi.llm.openai import OpenAIChat

from ai.settings import ai_settings
from hn_ai.search import search_web
from pdf_ai.storage import pdf_assistant_storage
from pdf_ai.tools import PDFTools
from pdf_ai.knowledge import get_pdf_knowledge_base_for_user
from utils.log import logger


def get_pdf_assistant(
    user_id: str,
    run_id: Optional[str] = None,
    debug_mode: bool = False,
) -> Assistant:
    pdf_tools = PDFTools(user_id=user_id)
    document_names_json: Optional[str] = pdf_tools.get_document_names()
    document_names: Optional[List] = json.loads(document_names_json) if document_names_json else None
    logger.info(f"Documents available: {document_names}")

    introduction = "Hi, I am PDF AI, built by [phidata](https://github.com/phidatahq/phidata)."

    instructions = [
        "You are made by phidata: https://github.com/phidatahq/phidata",
        f"You are interacting with the user: {user_id}",
        "You have a knowledge base of PDFs that you can use to answer questions.",
        "When the user asks a question, first determine if you can answer the question from the documents in the knowledge base.",
    ]
    if document_names is None or len(document_names) == 0:
        introduction += " Please upload a document to get started."
        instructions.append(
            "You do not have any documents in your knowledge base. Ask the user politely to upload a document and share a nice joke with them."
        )
    elif len(document_names) == 1:
        introduction += "\n\nAsk me about: {}".format(", ".join(document_names))
        instructions.extend(
            [
                f"You have the following documents in your knowledge base: {document_names}",
                "If the user asks a specific question, use the `search_latest_document` tool to search the latest document for context.",
                "If the user asks a summary, use the `get_latest_document_contents` tool to get the contents of the latest document.",
                "You can also search the entire knowledge base using the `search_knowledge_base` tool.",
            ]
        )
    else:
        introduction += "\n\nAsk me about: {}".format(", ".join(document_names))
        instructions.extend(
            [
                f"You have the following documents in your knowledge base: {document_names}",
                "When the user asks a question, first determine if you should search a specific document or the latest document uploaded by the user.",
                "If the user asks a specific question, use the `search_document` tool if you know the document to search OR `search_latest_document` tool to search the latest document for context.",
                "If the user asks to summarize a document, use the `get_document_contents` if you know the document to search OR `get_latest_document_contents` tool to get the contents of the latest document.",
            ]
        )
    instructions.extend(
        [
            "You can also search the entire knowledge base using the `search_knowledge_base` tool.",
            "Keep your conversation light hearted and fun.",
            "Using information from the document, provide the user with a concise and relevant answer.",
            "If the user asks what is this? they are asking about the latest document",
            "If you cannot find the information in the knowledge base, think if you can find it on the web. If you can find the information on the web, use the `search_web` tool",
            "When searching the knowledge base, search for at least 3 documents.",
            "When getting document contents, get atleast 3000 words so you get the first few pages.",
            "Most documents have a table of contents in the beginning so if you need those, use the `get_document_contents` tool.",
            "If the user compliments you, ask them to star phidata on GitHub: https://github.com/phidatahq/phidata",
        ]
    )

    return Assistant(
        name=f"pdf_assistant_{user_id}" if user_id else "hn_assistant",
        run_id=run_id,
        user_id=user_id,
        llm=OpenAIChat(
            model=ai_settings.gpt_4,
            max_tokens=ai_settings.default_max_tokens,
            temperature=ai_settings.default_temperature,
        ),
        storage=pdf_assistant_storage,
        monitoring=True,
        use_tools=True,
        introduction=introduction,
        tools=[search_web, pdf_tools],
        knowledge_base=get_pdf_knowledge_base_for_user(user_id),
        show_tool_calls=True,
        debug_mode=debug_mode,
        description="Your name is PDF AI and you are a chatbot that answers questions from a knowledge base of PDFs.",
        add_datetime_to_instructions=True,
        instructions=instructions,
        user_data={"documents": document_names},
    )
