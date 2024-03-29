from phi.storage.assistant.postgres import PgAssistantStorage

from db.session import db_url

arxiv_assistant_storage = PgAssistantStorage(
    schema="ai",
    db_url=db_url,
    table_name="arxiv_assistant",
)

latent_space_arxiv_bot_storage = PgAssistantStorage(
    schema="ai",
    db_url=db_url,
    table_name="latent_space_arxiv_bot",
)
