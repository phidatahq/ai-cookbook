from phi.assistant import Assistant
from phi.knowledge.pdf import PDFUrlKnowledgeBase
from phi.vectordb.pgvector import PgVector

from db.session import db_url

knowledge_base = PDFUrlKnowledgeBase(
    urls=["https://www.family-action.org.uk/content/uploads/2019/07/meals-more-recipes.pdf"],
    vector_db=PgVector(collection="recipes", db_url=db_url),
)
knowledge_base.load(recreate=False)

assistant = Assistant(
    knowledge_base=knowledge_base,
    function_calls=True,
    show_function_calls=True,
)

assistant.print_response("How do I make chicken tikka salad?")
assistant.print_response("What was my last question?")
