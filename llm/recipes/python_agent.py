from phi.agent.python import PythonAgent
from phi.file.local.csv import CsvFile

from workspace.settings import ws_settings

python_agent = PythonAgent(
    files=[CsvFile(
        description="Contains information about movies from IMDB.",
        path=str(ws_settings.ws_root.joinpath("data/csv/IMDB-Movie-Data.csv")),
    )],
    base_dir=ws_settings.ws_root.joinpath("pygpt/op"),
)

python_agent.cli_app()
# python_agent.print_response("What is the average rating of movies?")
# python_agent.print_response("Show me a chart of revenue over time")
