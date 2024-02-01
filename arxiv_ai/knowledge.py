import json
from typing import Optional

from phi.knowledge import AssistantKnowledge
from phi.embedder.openai import OpenAIEmbedder
from phi.vectordb.pgvector import PgVector2

from db.session import db_url
from utils.log import logger


def get_arxiv_summary_knowledge_base_for_user(user_id: Optional[str] = None) -> AssistantKnowledge:
    table_name = f"arxiv_summary_{user_id}" if user_id else "arxiv_summary"
    return AssistantKnowledge(
        vector_db=PgVector2(
            schema="ai",
            db_url=db_url,
            collection=table_name,
            embedder=OpenAIEmbedder(model="text-embedding-3-small"),
        ),
        num_documents=20,
    )


def get_arxiv_knowledge_base_for_user(user_id: Optional[str] = None) -> AssistantKnowledge:
    table_name = f"arxiv_knowledge_{user_id}" if user_id else "arxiv_knowledge"
    return AssistantKnowledge(
        vector_db=PgVector2(
            schema="ai",
            db_url=db_url,
            collection=table_name,
            embedder=OpenAIEmbedder(model="text-embedding-3-small"),
        ),
        num_documents=5,
    )

def get_available_docs(arxiv_kb: AssistantKnowledge, limit: int = 10) -> Optional[dict]:

    vector_db: PgVector2 = arxiv_kb.vector_db
    table = vector_db.table

    with vector_db.Session() as session, session.begin():
        try:
            query = session.query(table).distinct(table.c.name).limit(limit)
            result = session.execute(query)
            rows = result.fetchall()

            if rows is None:
                return "Sorry could not find any documents"

            document_names = []
            for row in rows:
                document_name = row.meta_data["title"]
                document_names.append(document_name)

            return document_names
        except Exception as e:
            logger.error(f"Error getting document names: {e}")
            return None
