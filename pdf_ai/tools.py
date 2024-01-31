import json
from typing import List, Optional

from phi.document import Document
from phi.tools import ToolRegistry
from phi.knowledge import AssistantKnowledge
from phi.vectordb.pgvector import PgVector2

from pdf_ai.knowledge import get_pdf_knowledge_base_for_user
from utils.log import logger


class PDFTools(ToolRegistry):
    def __init__(self, user_id: str):
        super().__init__(name="pdf_tools")

        self.user_id = user_id
        self.knowledge_base: AssistantKnowledge = get_pdf_knowledge_base_for_user(user_id=user_id)
        self.register(self.get_latest_document_contents)
        self.register(self.search_latest_document)
        self.register(self.search_document)
        self.register(self.get_document_contents)

    def get_latest_document_contents(self, limit: int = 5000) -> Optional[str]:
        """Use this function to get the content of the latest document uploaded by the user.

        Args:
            limit (int): Maximum number of characters to return. Defaults to 5000.

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

    def search_latest_document(self, query: str, num_chunks: int = 5) -> Optional[str]:
        """Use this function to search the latest document uploaded by the user for a query.

        Args:
            query (str): Query to search for
            num_chunks (int): Number of chunks to return. Defaults to 5.

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
            latest_document_query = session.query(table).order_by(table.c.created_at.desc()).limit(1)
            result = session.execute(latest_document_query)
            row = result.fetchone()

            if row is None:
                return "Sorry could not find latest document"

            latest_document_name = row.name
            logger.debug(f"Latest document name: {latest_document_name}")

        if latest_document_name is None:
            return "Sorry could not find latest document"

        search_results: List[Document] = vector_db.search(
            query=query, limit=num_chunks, filters={"name": latest_document_name}
        )
        logger.debug(f"Search result: {search_results}")

        if len(search_results) == 0:
            return "Sorry could not find any results from latest document"

        return json.dumps([doc.to_dict() for doc in search_results])

    def get_document_names(self, limit: int = 20) -> Optional[List[str]]:
        """Use this function to get the names of the documents uploaded by the user.

        Args:
            limit (int): Maximum number of documents to return. Defaults to 20.

        Returns:
            str: JSON string of the document names
        """

        logger.debug("Getting all document names")
        if self.knowledge_base.vector_db is None or not isinstance(self.knowledge_base.vector_db, PgVector2):
            return None

        vector_db: PgVector2 = self.knowledge_base.vector_db
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
                    document_name = row.name
                    document_names.append(document_name)

                return document_names
            except Exception as e:
                logger.error(f"Error getting document names: {e}")
                return None

    def search_document(self, query: str, document_name: str, num_chunks: int = 5) -> Optional[str]:
        """Use this function to search the latest document uploaded by the user for a query.

        Args:
            query (str): Query to search for
            num_chunks (int): Number of chunks to return. Defaults to 5.

        Returns:
            str: JSON string of the search results
        """

        logger.debug(f"Searching document {document_name} for query: {query}")
        if self.knowledge_base.vector_db is None or not isinstance(self.knowledge_base.vector_db, PgVector2):
            return "Sorry could not search latest document"

        search_results: List[Document] = self.knowledge_base.vector_db.search(
            query=query, limit=num_chunks, filters={"name": document_name}
        )
        logger.debug(f"Search result: {search_results}")

        if len(search_results) == 0:
            return "Sorry could not find any results from latest document"

        return json.dumps([doc.to_dict() for doc in search_results])

    def get_document_contents(self, document_name: str, limit: int = 5000) -> Optional[str]:
        """Use this function to get the content of the document with name=document_name.

        Args:
            limit (int): Maximum number of characters to return. Defaults to 5000.

        Returns:
            str: JSON string of the document contents
        """

        logger.debug(f"Getting document contents for user {document_name}")
        if self.knowledge_base.vector_db is None or not isinstance(self.knowledge_base.vector_db, PgVector2):
            return "Sorry could not find latest document"

        vector_db: PgVector2 = self.knowledge_base.vector_db
        table = vector_db.table
        with vector_db.Session() as session, session.begin():
            document_query = (
                session.query(table).filter(table.c.name == document_name).order_by(table.c.created_at.desc())
            )
            document_result = session.execute(document_query)
            document_rows = document_result.fetchall()
            document_content = ""
            for document_row in document_rows:
                document_content += document_row.content

            return document_content[:limit]

    # def get_document_introduction(self) -> Optional[str]:
    #     """Use this function to get a quick introduction to the documents uploaded by the user.
    #     This function will return a dictionary of document names and their first 200 characters.

    #     Returns:
    #         str: JSON string of the document names and their first 200 characters
    #     """

    #     logger.debug("Getting document introduction")
    #     if self.knowledge_base.vector_db is None or not isinstance(self.knowledge_base.vector_db, PgVector2):
    #         return None

    #     vector_db: PgVector2 = self.knowledge_base.vector_db
    #     table = vector_db.table
    #     with vector_db.Session() as session, session.begin():
    #         try:
    #             query = select(table.c.name, table.c.meta_data, table.c.content).order_by(table.c.created_at)
    #             result = session.execute(query)
    #             rows = result.fetchall()

    #             if rows is None:
    #                 return "Sorry could not find any documents"

    #             document_names = []
    #             for row in rows:
    #                 document_name = row.name
    #                 document_names.append(document_name)

    #             return document_names
    #         except Exception as e:
    #             logger.error(f"Error getting document names: {e}")
    #             return None
