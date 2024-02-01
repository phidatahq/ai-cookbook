import json
from io import BytesIO
from typing import List, Optional
from rich.pretty import pprint

import arxiv
import httpx
from pypdf import PdfReader
from phi.document import Document
from phi.tools import ToolRegistry
from phi.knowledge import AssistantKnowledge
from phi.document.reader.pdf import PDFUrlReader
from phi.vectordb.pgvector import PgVector2

from arxiv_ai.knowledge import get_arxiv_knowledge_base_for_user
from workspace.settings import ws_settings
from utils.log import logger


class ArxivTools(ToolRegistry):
    def __init__(self, user_id: str):
        super().__init__(name="pdf_tools")

        self.client: arxiv.Client = arxiv.Client()
        self.user_id: str = user_id
        self.knowledge_base: AssistantKnowledge = get_arxiv_knowledge_base_for_user(user_id=user_id)
        self.register(self.search_arxiv)

    def search_arxiv(self, query: str, max_results: int = 1) -> str:
        """
        Searches arXiv for a query.
        Args:
            query (str): The query to search arXiv for.
            max_results (int): The maximum number of results to return. Defaults to 5.

        Returns:
            str: JSON string of relevant documents from arXiv.
        """
        logger.debug(f"Searching arxiv for: {query}")

        all_documents = []
        document_summaries = []
        for result in self.client.results(search=arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance,
            sort_order=arxiv.SortOrder.Descending,
        )):
            try:
                result_documents = []
                meta_data = {
                    "title": result.title,
                    "entry_id": result.entry_id,
                    "updated": result.updated,
                    "authors": [author.name for author in result.authors],
                    "primary_category": result.primary_category,
                    "categories": result.categories,
                    "published": result.published.isoformat() if result.published else None,
                    "pdf_url": result.pdf_url,
                    "links": [link.href for link in result.links],
                    "summary": result.summary,
                    "comment": result.comment,
                }
                document_summaries.append(meta_data)

                if result.pdf_url:
                    logger.info(f"Downloading: {result.pdf_url}")
                    pdf_path = result.download_pdf(dirpath=str(ws_settings.storage_dir))
                    logger.info(f"Downloaded: {pdf_path}")
                    pdf_reader = PdfReader(pdf_path)
                    for page_number, page in enumerate(pdf_reader.pages, start=1):
                        page_content = page.extract_text()
                        if page_content:
                            _meta_data = meta_data.copy()
                            _meta_data["page"] = page_number
                            result_documents.append(
                                Document(
                                    id=result.entry_id,
                                    name=result.title,
                                    meta_data=_meta_data,
                                    content=page_content,
                                )
                            )

                if result_documents:
                    all_documents.extend(result_documents)
            except Exception as e:
                logger.error(f"Error creating document for paper {result.entry_id}: {e}")

        logger.info(f"Found {len(document_summaries)} documents: {query}")
        logger.info(f"Loading {len(all_documents)} documents for query: {query}")
        # pprint(all_documents)

        # logger.info("Adding Documents to knowledge base...")
        # # hn_knowledge_base.vector_db.delete()
        # hn_knowledge_base.load_documents(documents, upsert=True)
        # return f"Loaded {len(documents)} documents to HackerNews knowledge base."
        #
        # print(r.title)
        #
        # # from phi.document.reader.arxiv import ArxivReader
        #
        # # arxiv = ArxivReader(max_results=max_results)
        #
        # # relevant_docs: List[Document] = arxiv.read(query=query)
        # # return json.dumps([doc.to_dict() for doc in relevant_docs])

    def get_document_summaries(self, query: str, limit: int = 30) -> Optional[str]:
        """Use this function to get a summary of documents available in the knowledge base.

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

                return json.dumps(document_names)
            except Exception as e:
                logger.error(f"Error getting document names: {e}")
                return None
