from phi.storage.assistant.postgres import PgAssistantStorage

from db.session import db_url

hn_assistant_storage = PgAssistantStorage(
    schema="ai",
    db_url=db_url,
    table_name="hn_assistant",
)
