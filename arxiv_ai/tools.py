import json
from typing import List, Optional
from pathlib import Path

import arxiv
from pypdf import PdfReader
from phi.document import Document
from phi.tools import ToolRegistry
from phi.knowledge import AssistantKnowledge
from phi.vectordb.pgvector import PgVector2

from arxiv_ai.knowledge import get_arxiv_knowledge_base_for_user, get_arxiv_summary_knowledge_base_for_user
from workspace.settings import ws_settings
from utils.log import logger


class ArxivTools(ToolRegistry):
    def __init__(self, user_id: str):
        super().__init__(name="arxiv_tools")

        self.client: arxiv.Client = arxiv.Client()
        self.user_id: str = user_id
        self.summary_knowledge_base: AssistantKnowledge = get_arxiv_summary_knowledge_base_for_user(
            user_id=user_id
        )
        self.knowledge_base: AssistantKnowledge = get_arxiv_knowledge_base_for_user(user_id=user_id)
        self.storage_dir: Path = ws_settings.ws_root.joinpath(ws_settings.storage_dir)
        self.register(self.add_arxiv_papers_to_knowledge_base)
        self.register(self.search_arxiv_and_add_to_knowledge_base)
        self.register(self.get_document_summaries)
        self.register(self.search_document)
        self.register(self.get_document_contents)
        self.register(self.get_document_titles)
        if not self.storage_dir.exists():
            self.storage_dir.mkdir(parents=True, exist_ok=True)

    def add_arxiv_papers_to_knowledge_base(self, id_list: List[str]) -> str:
        """
        Use this function to add a list of arxiv papers to the knowledge base.

        Args:
            id_list (list, str): The list of `id` of the papers to add to the knowledge base.
            Should be of the format: ["2103.03404v1", "2103.03404v2"]

        Returns:
            str: If success or failure, returns a message.
        """
        logger.debug(f"Searching arxiv for: {id_list}")

        all_result_documents = []
        document_summaries = []
        for result in self.client.results(search=arxiv.Search(id_list=id_list)):
            try:
                result_documents = []
                meta_data = {
                    "title": result.title,
                    "name": result.get_short_id(),
                    "entry_id": result.entry_id,
                    "updated": result.updated.isoformat() if result.updated else None,
                    "authors": [author.name for author in result.authors],
                    "primary_category": result.primary_category,
                    "categories": result.categories,
                    "published": result.published.isoformat() if result.published else None,
                    "pdf_url": result.pdf_url,
                    "links": [link.href for link in result.links],
                }

                document_summary = meta_data.copy()
                document_summary["summary"] = result.summary
                document_summary["comment"] = result.comment
                document_summaries.append(
                    Document(
                        id=result.get_short_id(),
                        name=result.get_short_id(),
                        meta_data=meta_data,
                        content=json.dumps(document_summary),
                    )
                )

                result_documents.append(
                    Document(
                        id=result.get_short_id(),
                        name=result.get_short_id(),
                        meta_data=meta_data,
                        content=json.dumps(document_summary),
                    )
                )
                if result.pdf_url:
                    logger.info(f"Downloading: {result.pdf_url}")
                    pdf_path = result.download_pdf(dirpath=str(self.storage_dir))
                    logger.info(f"Downloaded: {pdf_path}")
                    pdf_reader = PdfReader(pdf_path)
                    for page_number, page in enumerate(pdf_reader.pages, start=1):
                        _page_content = page.extract_text()
                        if _page_content:
                            _meta_data = meta_data.copy()
                            _meta_data["page"] = page_number
                            _id = f"{result.get_short_id()}__{page_number}"
                            result_documents.append(
                                Document(
                                    id=_id,
                                    name=result.get_short_id(),
                                    meta_data=_meta_data,
                                    content=_page_content,
                                )
                            )

                if result_documents:
                    all_result_documents.extend(result_documents)
            except Exception as e:
                logger.error(f"Error creating document for paper {result.entry_id}: {e}")

        logger.info(f"Found {len(document_summaries)} results for: {id_list}")
        try:
            logger.info(f"Loading {len(all_result_documents)} documents for id_list: {id_list}")
            self.knowledge_base.load_documents(all_result_documents, upsert=True)

            logger.info(f"Loading {len(document_summaries)} document summaries for id_list: {id_list}")
            self.summary_knowledge_base.load_documents(document_summaries, upsert=True)
        except Exception as e:
            logger.error(f"Error loading documents for id_list: {id_list}: {e}")
            return f"Error loading documents for id: {id_list}: {e}"

        return json.dumps([doc.to_dict() for doc in document_summaries])

    def search_arxiv_and_add_to_knowledge_base(self, query: str, num_results: int = 5) -> str:
        """Use this function to adds papers from arXiv that match a string query.

        Args:
            query (str): The query to get arXiv papers for.
            num_results (int): The number of papers to add to knowledge base. Defaults to 10.

        Returns:
            str: A summary of the papers added to the knowledge base.
        """
        logger.debug(f"Searching arxiv for: {query}")

        all_result_documents = []
        document_summaries = []
        for result in self.client.results(
            search=arxiv.Search(
                query=query,
                max_results=num_results,
                sort_by=arxiv.SortCriterion.Relevance,
                sort_order=arxiv.SortOrder.Descending,
            )
        ):
            try:
                result_documents = []
                meta_data = {
                    "title": result.title,
                    "name": result.get_short_id(),
                    "entry_id": result.entry_id,
                    "updated": result.updated.isoformat() if result.updated else None,
                    "authors": [author.name for author in result.authors],
                    "primary_category": result.primary_category,
                    "categories": result.categories,
                    "published": result.published.isoformat() if result.published else None,
                    "pdf_url": result.pdf_url,
                    "links": [link.href for link in result.links],
                }

                document_summary = meta_data.copy()
                document_summary["summary"] = result.summary
                document_summary["comment"] = result.comment
                document_summaries.append(
                    Document(
                        id=result.get_short_id(),
                        name=result.get_short_id(),
                        meta_data=meta_data,
                        content=json.dumps(document_summary),
                    )
                )

                result_documents.append(
                    Document(
                        id=result.get_short_id(),
                        name=result.get_short_id(),
                        meta_data=meta_data,
                        content=json.dumps(document_summary),
                    )
                )
                if result.pdf_url:
                    logger.info(f"Downloading: {result.pdf_url}")
                    pdf_path = result.download_pdf(dirpath=str(self.storage_dir))
                    logger.info(f"Downloaded: {pdf_path}")
                    pdf_reader = PdfReader(pdf_path)
                    for page_number, page in enumerate(pdf_reader.pages, start=1):
                        _page_content = page.extract_text()
                        if _page_content:
                            _meta_data = meta_data.copy()
                            _meta_data["page"] = page_number
                            _id = f"{result.get_short_id()}__{page_number}"
                            result_documents.append(
                                Document(
                                    id=_id,
                                    name=result.get_short_id(),
                                    meta_data=_meta_data,
                                    content=_page_content,
                                )
                            )

                if result_documents:
                    all_result_documents.extend(result_documents)
            except Exception as e:
                logger.error(f"Error creating document for paper {result.entry_id}: {e}")

        logger.info(f"Found {len(document_summaries)} results for: {query}")
        try:
            logger.info(f"Loading {len(all_result_documents)} documents for query: {query}")
            self.knowledge_base.load_documents(all_result_documents, upsert=True)

            logger.info(f"Loading {len(document_summaries)} document summaries for query: {query}")
            self.summary_knowledge_base.load_documents(document_summaries, upsert=True)
        except Exception as e:
            logger.error(f"Error loading documents for query: {query}: {e}")
            return f"Error loading documents for query: {query}: {e}"

        return json.dumps([doc.to_dict() for doc in document_summaries])

    def get_document_summaries(self, query: str, limit: int = 10) -> Optional[str]:
        """Use this function to get a summary of documents available in the knowledge base.

        Args:
            query (str): The query to match document summaries with.
            limit (int): Maximum number of documents to return. Defaults to 30.

        Returns:
            str: JSON string of the document summaries
        """

        logger.debug(f"Getting summaries relevant to: {query}")
        try:
            relevant_documents = self.summary_knowledge_base.search(query=query, num_documents=limit)
            return json.dumps([doc.to_dict() for doc in relevant_documents])
        except Exception as e:
            logger.error(f"Error getting summaries for query: {query}: {e}")
            return "No documents found for query: {query}"

    def search_document(self, query: str, document_name: str, num_documents: int = 5) -> Optional[str]:
        """Use this function to search a particular arXiv document with name=document_name for a query.

        Args:
            query (str): Query to search for
            document_name (str): Name of the document to search
            num_documents (int): Number of results to return. Defaults to 5.

        Returns:
            str: JSON string of the search results
        """

        logger.debug(f"Searching document {document_name} for query: {query}")
        if self.knowledge_base.vector_db is None or not isinstance(self.knowledge_base.vector_db, PgVector2):
            return "Sorry could not search latest document"

        search_results: List[Document] = self.knowledge_base.vector_db.search(
            query=query, limit=num_documents, filters={"name": document_name}
        )
        logger.debug(f"Search result: {search_results}")

        if len(search_results) == 0:
            return f"Sorry could not find any results from document: {document_name}"

        return json.dumps([doc.to_dict() for doc in search_results])

    def get_document_contents(self, document_name: str, limit: int = 10000) -> Optional[str]:
        """Use this function to get the content of a particular arXiv document with name=document_name.

        Args:
            document_name (str): Name of the document to search. Eg: "1706.03762v7"
            limit (int): Maximum number of characters to return. Defaults to 10000.

        Returns:
            str: JSON string of the document contents
        """

        logger.debug(f"Getting document contents: {document_name}")
        if self.knowledge_base.vector_db is None or not isinstance(self.knowledge_base.vector_db, PgVector2):
            return "Vector DB not found."

        vector_db: PgVector2 = self.knowledge_base.vector_db
        table = vector_db.table
        try:
            with vector_db.Session() as session, session.begin():
                document_query = (
                    session.query(table)
                    .filter(table.c.name == document_name)
                    .order_by(table.c.created_at.desc())
                )
                document_result = session.execute(document_query)
                document_rows = document_result.fetchall()
                document_content = ""
                for document_row in document_rows:
                    document_content += document_row.content

                return document_content[:limit]
        except Exception as e:
            logger.error(f"Error getting document contents: {e}")
            logger.error("Table might not exist, creating for future use")
            vector_db.create()
            return ""

    def get_document_titles(self, limit: int = 20) -> Optional[str]:
        """Use this function to get the titles of the documents uploaded from ArXiv.

        Args:
            limit (int): Maximum number of documents to return. Defaults to 20.

        Returns:
            str: JSON string of the document names
        """

        logger.debug("Getting all document titles from the knowledge base.")
        if self.knowledge_base.vector_db is None or not isinstance(self.knowledge_base.vector_db, PgVector2):
            return "No documents found in the knowledge base."

        vector_db: PgVector2 = self.knowledge_base.vector_db
        table = vector_db.table
        with vector_db.Session() as session, session.begin():
            try:
                query = session.query(table).distinct(table.c.name).limit(limit)
                result = session.execute(query)
                rows = result.fetchall()

                if rows is None:
                    return "Sorry could not find any documents"

                document_titles = []
                for row in rows:
                    document_title = row.meta_data["title"]
                    document_titles.append(document_title)

                return json.dumps(document_titles)
            except Exception as e:
                logger.error(f"Error getting document names: {e}")
                return "No documents found in the knowledge base."
