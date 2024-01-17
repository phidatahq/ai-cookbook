from typing import List
from rich.pretty import pprint

from phi.assistant import AssistantRun
from ai.storage import pdf_assistant_storage


assistant_runs: List[AssistantRun] = pdf_assistant_storage.get_all_runs()
pprint(assistant_runs)
