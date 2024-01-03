import json
from typing import List, Optional

from pydantic import BaseModel
from phi.agent.duckdb import DuckDbAgent

from workspace.settings import ws_settings


class LocalTable(BaseModel):
    name: str
    columns: Optional[List[str]] = None
    description: str
    path: str


local_tables = [
    LocalTable(
        name="movies",
        description="Contains information about movies from IMDB.",
        path=str(ws_settings.ws_root.joinpath("data/csv/IMDB-Movie-Data.csv")),
    ),
]

duckdb_agent = DuckDbAgent(
    semantic_model=json.dumps(
        {
            "tables": [table.model_dump(exclude_none=True) for table in local_tables],
        },
        indent=4,
    ),
    debug_mode=True,
    base_dir=ws_settings.ws_root.joinpath("duckgpt/op"),
)

# duckdb_agent.cli_app()
# print(duckdb_agent.get_system_prompt())

duckdb_agent.print_response("What is the average rating of movies?")
