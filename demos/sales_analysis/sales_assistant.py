from phi.assistant.duckdb import DuckDbAssistant
from phi.knowledge.json import JSONKnowledgeBase
from phi.knowledge.text import TextKnowledgeBase
from phi.knowledge.combined import CombinedKnowledgeBase
from phi.vectordb.pgvector import PgVector
from phi.storage.assistant.postgres import PgAssistantStorage

from db.session import db_url
from workspace.settings import ws_settings

sales_knowledge_dir = ws_settings.ws_root.joinpath("demos", "sales_analysis", "knowledge")

sales_ai_knowledge_base = CombinedKnowledgeBase(
    # Build a sales knowledge base using text and json files
    sources=[
        TextKnowledgeBase(path=sales_knowledge_dir),
        JSONKnowledgeBase(path=sales_knowledge_dir),
    ],
    # Store the knowledge in `ai.sales_knowledge`
    vector_db=PgVector(collection="sales_knowledge", db_url=db_url),
)
sales_ai_knowledge_base.load(recreate=False)

sales_ai_storage = PgAssistantStorage(table_name="sales_assistant", db_url=db_url)

sales_ai = DuckDbAssistant(
    name="sales_ai",
    storage=sales_ai_storage,
    knowledge_base=sales_ai_knowledge_base,
    monitoring=True,
    use_tools=True,
    show_tool_calls=True,
    debug_mode=True,
    base_dir=ws_settings.ws_root.joinpath("demos", "sales_analysis", "queries"),
)

sales_ai.print_response(
    "Categorize customers into groups based on the Recency, Frequency, and Monetary value model."
)
