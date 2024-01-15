from phi.assistant.openai import OpenAIAssistant
from phi.assistant.openai.file.url import UrlFile
from phi.assistant.openai.file.local import LocalFile
from phi.assistant.openai.tool import CodeInterpreter

imdb_movie_data_s3 = UrlFile(
    url="https://phi-public.s3.amazonaws.com/imdb/IMDB-Movie-Data.csv"
).get_or_create()
# imdb_movie_data_local = LocalFile(path="data/csv/IMDB-Movie-Data.csv").get_or_create()

with OpenAIAssistant(
    name="CsvAssistant",
    tools=[CodeInterpreter],
    files=[imdb_movie_data_s3],
    instructions="You are an expert at analyzing CSV data. Whenever you run an analysis, explain each step.",
) as csv_ai:
    csv_ai.print_response("Who is the most popular actor by votes?")
