from typing import Optional, List, Tuple

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


def get_available_docs(summary_knowledge_base: AssistantKnowledge) -> Optional[List[Tuple[str, str]]]:
    if summary_knowledge_base.vector_db is None or not isinstance(
        summary_knowledge_base.vector_db, PgVector2
    ):
        return None

    vector_db = summary_knowledge_base.vector_db
    table = vector_db.table
    with vector_db.Session() as session, session.begin():
        try:
            query = session.query(table)
            result = session.execute(query)
            rows = result.fetchall()

            if rows is None:
                return None

            documents = []
            for row in rows:
                document_id = row.id
                document_title = row.meta_data["title"]
                documents.append((document_id, document_title))
            return documents
        except Exception as e:
            logger.error(f"Error getting document names: {e}")
            return None
