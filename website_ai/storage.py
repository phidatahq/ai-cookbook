from phi.storage.assistant.postgres import PgAssistantStorage

from db.session import db_url

website_assistant_storage = PgAssistantStorage(
    schema="ai",
    db_url=db_url,
    table_name="website_assistant",
)
