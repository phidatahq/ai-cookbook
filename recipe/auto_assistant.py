from phi.assistant import Assistant
from phi.knowledge.pdf import PDFUrlKnowledgeBase
from phi.vectordb.pgvector import PgVector2

from db.session import db_url

knowledge_base = PDFUrlKnowledgeBase(
    urls=["https://phi-public.s3.amazonaws.com/recipes/ThaiRecipes.pdf"],
    vector_db=PgVector2(collection="recipes", db_url=db_url),
)
knowledge_base.load(recreate=False)

assistant = Assistant(
    knowledge_base=knowledge_base,
    use_tools=True,
    show_tool_calls=True,
)

assistant.print_response("How do I make chicken tikka salad?")
assistant.print_response("What was my last question?")
