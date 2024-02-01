from typing import Optional

from phi.knowledge import AssistantKnowledge
from phi.embedder.openai import OpenAIEmbedder
from phi.vectordb.pgvector import PgVector2

from db.session import db_url


def get_arxiv_knowledge_base_for_user(user_id: Optional[str] = None) -> AssistantKnowledge:
    table_name = f"arxiv_documents_{user_id}" if user_id else "arxiv_documents"
    return AssistantKnowledge(
        vector_db=PgVector2(
            schema="ai",
            db_url=db_url,
            collection=table_name,
            embedder=OpenAIEmbedder(model="text-embedding-3-small"),
        ),
        num_documents=5,
    )
