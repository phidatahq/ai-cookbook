import typer
from rich.prompt import Prompt
from typing import Optional, List

from phi.conversation import Conversation
from phi.storage.conversation.postgres import PgConversationStorage
from phi.knowledge.pdf import PDFUrlKnowledgeBase
from phi.vectordb.pgvector import PgVector

from db.session import db_url

knowledge_base = PDFUrlKnowledgeBase(
    urls=["https://www.family-action.org.uk/content/uploads/2019/07/meals-more-recipes.pdf"],
    vector_db=PgVector(collection="recipes", db_url=db_url),
)

storage = PgConversationStorage(table_name="recipe_conversations", db_url=db_url)


def llm_app(new: bool = False, user: str = "user"):
    conversation_id: Optional[str] = None

    if not new:
        existing_conversation_ids: List[str] = storage.get_all_conversation_ids(user)
        if len(existing_conversation_ids) > 0:
            conversation_id = existing_conversation_ids[0]

    conversation = Conversation(
        user_name=user,
        id=conversation_id,
        knowledge_base=knowledge_base,
        storage=storage,
        function_calls=True,
        show_function_calls=True,
    )
    if conversation_id is None:
        conversation_id = conversation.id
        print(f"Started Conversation: {conversation_id}\n")
    else:
        print(f"Continuing Conversation: {conversation_id}\n")

    # -*- If you want to load the knowledge base, uncomment the following line
    # conversation.knowledge_base.load(recreate=False)
    while True:
        message = Prompt.ask(f"[bold] :sunglasses: {user} [/bold]")
        if message in ("exit", "bye"):
            break
        conversation.print_response(message)


if __name__ == "__main__":
    typer.run(llm_app)
