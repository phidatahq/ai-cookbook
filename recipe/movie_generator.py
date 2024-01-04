from typing import List
from pydantic import BaseModel, Field
from phi.conversation import Conversation
from rich.pretty import pprint


class MovieScript(BaseModel):
    setting: str = Field(..., description="Setting of the movie. If not available, provide a random setting.")
    ending: str = Field(..., description="Ending of the movie. If not available, provide a happy ending.")
    genre: str = Field(
        ..., description="Genre of the movie. If not available, select action, thriller or romantic comedy."
    )
    name: str = Field(..., description="Give a name to this movie")
    characters: List[str] = Field(..., description="Name of characters for this movie.")
    storyline: str = Field(..., description="2 sentence story of the movie.")


movie_generator = Conversation(
    system_prompt="Generate a movie",
    output_model=MovieScript,
)

pprint(movie_generator.run("New York"))
