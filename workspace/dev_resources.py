from os import getenv

from phi.docker.app.fastapi import FastApi
from phi.docker.app.postgres import PgVectorDb
from phi.docker.app.streamlit import Streamlit
from phi.docker.resources import DockerResources
from phi.docker.resource.image import DockerImage

from workspace.jupyter.lab import dev_jupyter_app
from workspace.settings import ws_settings

#
# -*- Resources for the Development Environment
#

# -*- Dev image
dev_image = DockerImage(
    name=f"{ws_settings.image_repo}/{ws_settings.ws_name}",
    tag=ws_settings.dev_env,
    enabled=ws_settings.build_images,
    path=str(ws_settings.ws_root),
    pull=ws_settings.force_pull_images,
    # Uncomment to push the dev image
    # push_image=ws_settings.push_images,
    skip_docker_cache=ws_settings.skip_image_cache,
)

# -*- Dev database running on port 5432:5432
dev_db = PgVectorDb(
    name=f"db-{ws_settings.ws_name}",
    enabled=ws_settings.dev_db_enabled,
    pg_user="pdf_user",
    pg_password="pdf_password",
    pg_database="app_db",
    # Connect to this db on port 5432
    host_port=5555,
    debug_mode=True,
)

# -*- Build container environment
container_env = {
    "RUNTIME_ENV": "dev",
    # Get the OpenAI API key from the local environment
    "OPENAI_API_KEY": getenv("OPENAI_API_KEY"),
    # Database configuration
    "DB_HOST": dev_db.get_db_host(),
    "DB_PORT": dev_db.get_db_port(),
    "DB_USER": dev_db.get_db_user(),
    "DB_PASS": dev_db.get_db_password(),
    "DB_DATABASE": dev_db.get_db_database(),
    # Wait for database to be available before starting the application
    "WAIT_FOR_DB": ws_settings.dev_db_enabled,
    # Migrate database on startup using alembic
    # "MIGRATE_DB": ws_settings.prd_db_enabled,
}

# -*- Streamlit running on port 8501:8501
dev_streamlit = Streamlit(
    name=f"app-{ws_settings.ws_name}",
    enabled=ws_settings.dev_app_enabled,
    image=dev_image,
    command="streamlit run app/Home.py",
    port_number=8501,
    debug_mode=True,
    mount_workspace=True,
    streamlit_server_headless=True,
    env_vars=container_env,
    use_cache=ws_settings.use_cache,
    # Read secrets from secrets/dev_app_secrets.yml
    secrets_file=ws_settings.ws_root.joinpath("workspace/secrets/dev_app_secrets.yml"),
    depends_on=[dev_db],
)

# -*- Hackernews App running on port 8501:8501
hn_ai = Streamlit(
    name=f"hn-{ws_settings.ws_name}",
    image=dev_image,
    enabled=getenv("HACKERNEWS_AI", False),
    command="streamlit run hn_ai/app.py",
    host_port=8502,
    container_port=8501,
    debug_mode=True,
    mount_workspace=True,
    streamlit_server_headless=True,
    env_vars=container_env,
    use_cache=ws_settings.use_cache,
    # Read secrets from secrets/dev_app_secrets.yml
    secrets_file=ws_settings.ws_root.joinpath("workspace/secrets/dev_app_secrets.yml"),
    depends_on=[dev_db],
)

# -*- FastApi running on port 8000:8000
dev_fastapi = FastApi(
    name=f"api-{ws_settings.ws_name}",
    enabled=ws_settings.dev_api_enabled,
    image=dev_image,
    command="uvicorn api.main:app --reload",
    port_number=8000,
    debug_mode=True,
    mount_workspace=True,
    env_vars=container_env,
    use_cache=ws_settings.use_cache,
    # Read secrets from secrets/dev_app_secrets.yml
    secrets_file=ws_settings.ws_root.joinpath("workspace/secrets/dev_app_secrets.yml"),
    depends_on=[dev_db],
)

# -*- Update jupyter environment variables
dev_jupyter_app.env_vars = container_env

# -*- Dev DockerResources
dev_docker_resources = DockerResources(
    env=ws_settings.dev_env,
    network=ws_settings.ws_name,
    apps=[dev_db, dev_streamlit, hn_ai, dev_fastapi, dev_jupyter_app],
)
