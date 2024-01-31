import json
from typing import List, Optional

from phi.document import Document
from phi.tools import ToolRegistry
from phi.knowledge import AssistantKnowledge
from phi.vectordb import VectorDb
from phi.vectordb.pgvector import PgVector2

from pdf_ai.knowledge import get_pdf_knowledge_base_for_user
from utils.log import logger


class WebsiteTools(ToolRegistry):
    def __init__(self, user_id: str):
        super().__init__(name="pdf_tools")

        self.user_id = user_id
        self.knowledge_base: AssistantKnowledge = get_pdf_knowledge_base_for_user(user_id=user_id)
        self.register(self.get_latest_document_contents)
        self.register(self.search_latest_document)

    def get_latest_document_contents(self, limit: int = 5000) -> Optional[str]:
        """Use this function to get the content of the latest document uploaded by the user.

        Args:
            limit (int, optional): Maximum number of characters to return. Defaults to 5000.

        Returns:
            str: JSON string of the latest document
        """

        logger.debug(f"Getting latest document for user {self.user_id}")
        if self.knowledge_base.vector_db is None or not isinstance(self.knowledge_base.vector_db, PgVector2):
            return "Sorry could not find latest document"

        vector_db: PgVector2 = self.knowledge_base.vector_db
        table = vector_db.table
        with vector_db.Session() as session, session.begin():
            query = session.query(table).order_by(table.c.created_at.desc()).limit(1)
            result = session.execute(query)
            row = result.fetchone()

            if row is None:
                return "Sorry could not find latest document"

            latest_document_name = row.name
            logger.debug(f"Latest document name: {latest_document_name}")

            document_query = session.query(table).filter(table.c.name == latest_document_name)
            document_result = session.execute(document_query)
            document_rows = document_result.fetchall()
            latest_document_content = ""
            for document_row in document_rows:
                document_content = document_row.content
                latest_document_content += document_content

            return latest_document_content[:limit]

        return "Sorry could not find latest document"

    def search_latest_document(self, query: str, num_documents: Optional[int] = None) -> Optional[str]:
        """Use this function to search the latest document uploaded by the user for a query.

        Args:
            query (str): Query to search for
            num_documents (Optional[int], optional): Number of documents to return. Defaults to None.

        Returns:
            str: JSON string of the search results
        """

        logger.debug(f"Searching latest document for query: {query}")
        if self.knowledge_base.vector_db is None or not isinstance(self.knowledge_base.vector_db, PgVector2):
            return "Sorry could not search latest document"

        vector_db: PgVector2 = self.knowledge_base.vector_db
        table = vector_db.table
        latest_document_name = None
        with vector_db.Session() as session, session.begin():
            query = session.query(table).order_by(table.c.created_at.desc()).limit(1)
            result = session.execute(query)
            row = result.fetchone()

            if row is None:
                return "Sorry could not find latest document"

            latest_document_name = row.name
            logger.debug(f"Latest document name: {latest_document_name}")

        if latest_document_name is None:
            return "Sorry could not find latest document"

        search_results: List[Document] = vector_db.search(
            query=query, limit=num_documents, filters={"name": latest_document_name}
        )
        logger.debug(f"Search result: {search_results}")

        if len(search_results) == 0:
            return "Sorry could not find any results from latest document"

        return json.dumps([doc.to_dict() for doc in search_results])
