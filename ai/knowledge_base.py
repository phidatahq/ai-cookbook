from phi.knowledge.combined import CombinedKnowledgeBase
from phi.knowledge.pdf import PDFUrlKnowledgeBase, PDFKnowledgeBase
from phi.knowledge.website import WebsiteKnowledgeBase
from phi.vectordb.pgvector import PgVector

from db.session import db_url

url_pdf_knowledge_base = PDFUrlKnowledgeBase(
    urls=["https://www.family-action.org.uk/content/uploads/2019/07/meals-more-recipes.pdf"],
    # Store this knowledge base in ai.url_pdf_documents
    vector_db=PgVector(
        schema="ai",
        db_url=db_url,
        collection="url_pdf_documents",
    ),
    # 2 references are added to the prompt
    num_documents=2,
)

local_pdf_knowledge_base = PDFKnowledgeBase(
    path="data/pdfs",
    # Store this knowledge base in ai.local_pdf_documents
    vector_db=PgVector(
        schema="ai",
        db_url=db_url,
        collection="local_pdf_documents",
    ),
    # 3 references are added to the prompt
    num_documents=3,
)

pdf_knowledge_base = CombinedKnowledgeBase(
    sources=[
        url_pdf_knowledge_base,
        local_pdf_knowledge_base,
    ],
    # Store this knowledge base in ai.pdf_documents
    vector_db=PgVector(
        schema="ai",
        db_url=db_url,
        collection="pdf_documents",
    ),
    # 2 references are added to the prompt
    num_documents=2,
)

website_knowledge_base = WebsiteKnowledgeBase(
    urls=["https://docs.phidata.com/introduction"],
    # Number of links to follow from the seed URLs
    max_links=15,
    # Store this knowledge base in ai.website_documents
    vector_db=PgVector(
        schema="ai",
        db_url=db_url,
        collection="website_documents",
    ),
    # 3 references are added to the prompt
    num_documents=3,
)
