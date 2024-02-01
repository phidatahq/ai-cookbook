from phi.utils.log import set_log_level_to_debug

from arxiv_ai.tools import ArxivTools

set_log_level_to_debug()
arxiv_tools = ArxivTools(user_id="ab")

search_results = arxiv_tools.search_arxiv(query="The FlashAttention Paper")
print(search_results)
