from langchain_community.document_loaders.csv_loader import CSVLoader

from workspace.settings import ws_settings

movies_file_path = ws_settings.ws_root.joinpath("data/csv/IMDB-Movie-Data.csv")
loader = CSVLoader(str(movies_file_path))
data = loader.load()

print(data)
