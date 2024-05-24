from phi.knowledge.website import WebsiteKnowledgeBase
from phi.vectordb.pgvector import PgVector2

db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"

knowledge_base = WebsiteKnowledgeBase(
    urls=["https://docs.phidata.com/introduction"],
    max_links=10,
    vector_db=PgVector2(
        collection="phidata_website",
        db_url= db_url,
    ),
)
    