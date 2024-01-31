from typing import Optional

from phi.knowledge.website import WebsiteKnowledgeBase
from phi.embedder.openai import OpenAIEmbedder
from phi.vectordb.pgvector import PgVector2

from db.session import db_url
from utils.log import logger


def get_website_knowledge_base_for_user(user_id: Optional[str] = None) -> WebsiteKnowledgeBase:
    table_name = f"website_documents_{user_id}" if user_id else "website_documents"
    return WebsiteKnowledgeBase(
        vector_db=PgVector2(
            schema="ai",
            db_url=db_url,
            collection=table_name,
            embedder=OpenAIEmbedder(model="text-embedding-3-small"),
        ),
        num_documents=5,
    )
